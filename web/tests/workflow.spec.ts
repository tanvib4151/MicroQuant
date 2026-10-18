import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
const dir = mkdtempSync(join(tmpdir(), "neuroquant-test-"));
const python = process.env.TEST_PYTHON || "python3";
test.beforeAll(() => {
  execFileSync(python, [
    "-c",
    `from PIL import Image
import numpy as np
from pathlib import Path
p=Path(${JSON.stringify(dir)})
a=np.zeros((100,100,3),np.uint8);a[:50,:50,1]=200;a[:,:,0]=200
Image.fromarray(a).save(p/'rgb.png')
a=np.array([[0,256,1000,65535]],np.uint16);Image.fromarray(a).save(p/'gray16.png')
a=np.zeros((100,100),np.uint8);a[:50,:50]=200;Image.fromarray(a).save(p/'gray.png')
`,
  ]);
});
test.afterAll(() => rmSync(dir, { recursive: true, force: true }));
test("complete scientific workflow and exports", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "NeuroQuant" })).toBeVisible();
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "rgb.png"));
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.getByRole("button", { name: "Reset to entire image" }).click();
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.getByPlaceholder("e.g. Iba1").fill("Iba1");
  await expect(
    page.getByRole("definition").filter({ hasText: "Iba1" }),
  ).toBeVisible();
  await page.getByLabel("Intensity channel").selectOption("red");
  await expect(page.getByTestId("positive-area")).toHaveText("100.000%");
  await page.getByLabel("Intensity channel").selectOption("green");
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.getByLabel("Lower threshold", { exact: true }).fill("201");
  await expect(page.getByTestId("positive-area")).toHaveText("0.000%");
  await page.getByLabel("Lower threshold", { exact: true }).fill("100");
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.getByLabel("ROI x1").fill("50");
  await page.getByLabel("ROI y1").fill("50");
  await expect(page.getByTestId("positive-area")).toHaveText("100.000%");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Results CSV" }).click();
  const csv = await downloadPromise;
  const text = readFileSync((await csv.path())!, "utf8");
  expect(text).toContain("Iba1");
  expect(text).toContain("2500");
  const jsonPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Settings JSON" }).click();
  const json = JSON.parse(
    readFileSync((await (await jsonPromise).path())!, "utf8"),
  );
  expect(json.positive_pixels).toBe(2500);
  expect(json.roi).toEqual({ x0: 0, y0: 0, x1: 50, y1: 50 });
  expect(json.lower_threshold).toBe(100);
  expect(json.sha256).toHaveLength(64);
  const pngPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Overlay PNG" }).click();
  const png = readFileSync((await (await pngPromise).path())!);
  expect(png.readUInt32BE(16)).toBe(100);
  expect(png.readUInt32BE(20)).toBe(100);
  await page.getByRole("button", { name: "Reset to entire image" }).click();
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  const surface = page.getByTestId("roi-surface");
  await surface.scrollIntoViewIfNeeded();
  const bounds = (await surface.boundingBox())!;
  await page.mouse.move(bounds.x, bounds.y);
  await page.mouse.down();
  await page.mouse.move(
    bounds.x + bounds.width / 2,
    bounds.y + bounds.height / 2,
  );
  await page.mouse.up();
  await expect(page.getByLabel("ROI x1")).toHaveValue("50");
  await expect(page.getByLabel("ROI y1")).toHaveValue("50");
  await expect(page.getByTestId("positive-area")).toHaveText("100.000%");
  await page.getByLabel("Overlay opacity").fill("0.9");
  await expect(page.getByTestId("positive-area")).toHaveText("100.000%");
  await page.getByLabel("Image source").selectOption("published");
  await expect(
    page.getByText("Published figures may be adjusted", { exact: false }),
  ).toBeVisible();
});
test("uint16 raw intensities and grayscale reset", async ({ page }) => {
  await page.goto("/");
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray16.png"));
  await expect(page.getByLabel("Upper threshold", { exact: true })).toHaveValue(
    "65535",
  );
  await expect(page.getByTestId("positive-area")).toHaveText("75.000%");
  await page.getByLabel("Lower threshold", { exact: true }).fill("1000");
  await expect(page.getByTestId("positive-area")).toHaveText("50.000%");
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray.png"));
  await expect(page.getByLabel("Upper threshold", { exact: true })).toHaveValue(
    "255",
  );
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
});
test("invalid upload and backend failure are understandable", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Upload microscopy image").setInputFiles({
    name: "bad.png",
    mimeType: "image/png",
    buffer: Buffer.from("corrupt"),
  });
  await expect(page.locator("p[role=alert]")).toContainText("Cannot decode");
  await expect(page.getByTestId("positive-area")).toHaveCount(0);
  await page.route("**/api/analyze", (route) =>
    route.fulfill({
      status: 502,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Cannot reach the analysis engine." }),
    }),
  );
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray.png"));
  await expect(page.locator("p[role=alert]")).toContainText("Cannot reach");
});
test("older response cannot overwrite a newer threshold", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray.png"));
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.route("**/api/analyze", async (route) => {
    const lower = Number(
      route
        .request()
        .postData()
        ?.match(/name="lower_threshold"\r\n\r\n(\d+)/)?.[1],
    );
    const response = await request.post("/api/analyze", {
      multipart: {
        image: {
          name: "gray.png",
          mimeType: "image/png",
          buffer: readFileSync(join(dir, "gray.png")),
        },
        channel: "gray",
        lower_threshold: String(lower),
        upper_threshold: "255",
      },
    });
    const body = await response.json();
    if (body.lower_threshold === 201)
      await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.fulfill({ response, json: body }).catch(() => {});
  });
  await page.getByLabel("Lower threshold", { exact: true }).fill("201");
  await page.waitForTimeout(400);
  await page.getByLabel("Lower threshold", { exact: true }).fill("100");
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.waitForTimeout(1200);
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
});

test("automatic Otsu selects raw ROI thresholds, exports method, and recovers from uniform ROI", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray.png"));
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await page.getByLabel("Threshold method").selectOption("otsu");
  await expect(
    page.getByRole("definition").filter({ hasText: "Auto: Otsu" }),
  ).toBeVisible();
  await expect(page.getByLabel("Lower threshold", { exact: true })).toHaveValue(
    "1",
  );
  await expect(
    page.getByLabel("Lower threshold", { exact: true }),
  ).toBeDisabled();
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  const jsonPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Settings JSON" }).click();
  const settings = JSON.parse(
    readFileSync((await (await jsonPromise).path())!, "utf8"),
  );
  expect(settings.threshold_method).toBe("otsu");
  expect(settings.lower_threshold).toBe(1);
  expect(settings.upper_threshold).toBe(255);
  await page.getByLabel("ROI x0").fill("50");
  await expect(page.locator("p[role=alert]")).toContainText(
    "at least two distinct intensities",
  );
  await expect(page.getByRole("button", { name: "Settings JSON" })).toHaveCount(
    0,
  );
  await page.getByLabel("Threshold method").selectOption("manual");
  await expect(
    page.getByLabel("Lower threshold", { exact: true }),
  ).toBeEnabled();
  await expect(page.getByTestId("positive-area")).toHaveText("0.000%");
});

test("provenance, QC definitions and research checklist persist with current exports", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray.png"));
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  await expect(
    page.getByRole("heading", { name: "Threshold-positive ROI area" }),
  ).toBeVisible();
  await expect(
    page.getByText("Pixels at datatype maximum", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Zero does not exclude detector clipping.", {
      exact: false,
    }),
  ).toBeVisible();
  await page.getByLabel("Image source").selectOption("published");
  await page
    .getByText("Provenance and controls (optional)", { exact: true })
    .click();
  await page.getByLabel("Sample / specimen ID").fill("animal-07 / section-03");
  await page
    .getByLabel("Acquisition notes")
    .fill("Exposure 30 ms, gain 2; detector ceiling 4095");
  await page.getByLabel("Control reference").fill("negative-01");
  await expect(page.getByTestId("positive-area")).toHaveText("25.000%");
  const jsonPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Settings JSON" }).click();
  const settings = JSON.parse(
    readFileSync((await (await jsonPromise).path())!, "utf8"),
  );
  expect(settings.image_source).toBe("published");
  expect(settings.sample_id).toBe("animal-07 / section-03");
  expect(settings.control_reference).toBe("negative-01");
  expect(settings.acquisition_notes).toContain("4095");
  expect(
    settings.warnings.some((n: string) => n.includes("Published-figure")),
  ).toBeTruthy();
  expect(
    settings.interpretation_notes.some((n: string) => n.includes("validation")),
  ).toBeTruthy();
  expect(settings.datatype_max_fraction).toBe(0);
  const csvPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Results CSV" }).click();
  const csv = readFileSync((await (await csvPromise).path())!, "utf8");
  expect(csv).toContain("image_source");
  expect(csv).toContain("published");
  expect(csv).toContain("negative-01");
  expect(csv).toContain("Published-figure");
  expect(csv).toContain("interpretation_notes");
  await page
    .getByText("Before biological interpretation", { exact: true })
    .click();
  await expect(
    page.getByText(
      "Biological validation pending. This checklist is guidance, not certification.",
    ),
  ).toBeVisible();
  await page
    .getByLabel("Upload microscopy image")
    .setInputFiles(join(dir, "gray16.png"));
  await expect(page.getByTestId("positive-area")).toHaveText("75.000%");
  await expect(page.getByLabel("Image source")).toHaveValue("unspecified");
  await expect(page.getByLabel("Sample / specimen ID")).toHaveValue("");
  await expect(page.getByLabel("Control reference")).toHaveValue("");
});
