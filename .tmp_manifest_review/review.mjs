import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/miyur/Downloads/manifiesto_miyu_y_vera_sin_cortes.xlsx";
const outputDir = "C:/Github/inflacion/.tmp_manifest_review/rendered";

await fs.mkdir(outputDir, { recursive: true });
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const overview = await workbook.inspect({
  kind: "workbook,sheet,table,drawing",
  maxChars: 12000,
  tableMaxRows: 12,
  tableMaxCols: 12,
  tableMaxCellChars: 160,
});
console.log("=== OVERVIEW ===");
console.log(overview.ndjson);

for (const sheet of workbook.worksheets.items) {
  const used = sheet.getUsedRange();
  console.log(`=== SHEET ${sheet.name} ===`);
  console.log(JSON.stringify({
    name: sheet.name,
    address: used?.address ?? null,
    values: used?.values ?? [],
    formulas: used?.formulas ?? [],
  }));

  const safeName = sheet.name.replace(/[^a-z0-9_-]+/gi, "_");
  const preview = await workbook.render({
    sheetName: sheet.name,
    autoCrop: "all",
    scale: 1.4,
    format: "png",
  });
  await fs.writeFile(
    path.join(outputDir, `${safeName}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log("=== ERRORS ===");
console.log(errors.ndjson);
