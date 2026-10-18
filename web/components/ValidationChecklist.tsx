export default function ValidationChecklist() {
  return (
    <details className="validation-checklist">
      <summary>Before biological interpretation</summary>
      <p>
        Biological validation pending. This checklist is guidance, not
        certification.
      </p>
      <ol>
        <li>
          Use original lossless images. Record marker/channel, acquisition
          settings and any upstream processing.
        </li>
        <li>
          Review appropriate negative, positive and autofluorescence controls;
          consider secondary-only and single-label controls where applicable.
        </li>
        <li>
          Predefine anatomical ROI and exclusion rules. Rectangle area is not
          automatically tissue area.
        </li>
        <li>
          Justify thresholds independently of desired group outcomes. Otsu also
          splits background variation.
        </li>
        <li>
          Check detector clipping using acquisition metadata; zero pixels at the
          datatype maximum does not exclude saturation.
        </li>
        <li>
          Compare identical channels, pixels, ROIs and bounds in Fiji, and
          record discrepancies.
        </li>
        <li>
          Review overlays blinded to group where feasible. Preserve provenance
          and QC notes in exports.
        </li>
      </ol>
      <p>
        Do not infer cell counts, biological activation or barrier permeability
        from threshold-positive area alone. Biological replicates must be
        defined independently of pixels and fields.
      </p>
    </details>
  );
}
