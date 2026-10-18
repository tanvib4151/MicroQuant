import { NextRequest, NextResponse } from "next/server";
export const runtime = "nodejs";
export const maxDuration = 60;
export async function POST(request: NextRequest) {
  const limit = Number(process.env.MAX_UPLOAD_BYTES || 20971520) + 65536;
  if (Number(request.headers.get("content-length")) > limit)
    return NextResponse.json(
      { detail: "Upload exceeds the configured byte limit." },
      { status: 413 },
    );
  try {
    // Bound streaming input even when Content-Length is absent or incorrect.
    const reader = request.body?.getReader();
    if (!reader)
      return NextResponse.json({ detail: "Missing upload." }, { status: 400 });
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) {
        await reader.cancel();
        return NextResponse.json(
          { detail: "Upload exceeds the configured byte limit." },
          { status: 413 },
        );
      }
      chunks.push(value);
    }
    const body = Buffer.concat(chunks);
    const response = await fetch(
      `${process.env.API_BASE_URL || "http://127.0.0.1:8000"}/analyze`,
      {
        method: "POST",
        body,
        headers: { "Content-Type": request.headers.get("content-type") || "" },
        signal: AbortSignal.timeout(60000),
        cache: "no-store",
      },
    );
    return new NextResponse(await response.text(), {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Cannot reach the analysis engine, or the request timed out. Check that FastAPI is running.",
      },
      { status: 502 },
    );
  }
}
