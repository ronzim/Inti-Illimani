const fs = require('fs');
const path = require('path');
const xlsx = require('xlsx');

function loadAndParse(filename) {
    if (!fs.existsSync(filename)) {
        console.log("File not found:", filename);
        return [];
    }
    const wb = xlsx.readFile(filename);
    const sheet = wb.Sheets[wb.SheetNames[0]];
    const rawData = xlsx.utils.sheet_to_json(sheet);

    const parsedData = [];

    // Start from index 1 to skip the header row, it seems row 0 is english mapping
    for (let i = 1; i < rawData.length; i++) {
        const row = rawData[i];

        let rawKp = row['meters'];
        let rawLat = row['Latitude'];
        let rawLng = row['Longitude'] || row['Longitude '];
        let rawDepth = row['Depth of wall loss'];
        let rawPof = row['Probability of failure'];

        if (rawLat === undefined || rawLng === undefined) continue;

        const kp = parseFloat(rawKp) || 0;
        const latVal = parseFloat(rawLat);
        const lngVal = parseFloat(rawLng);

        if (isNaN(latVal) || isNaN(lngVal)) continue;

        const depth = parseFloat(rawDepth) || 0;
        const pof = parseFloat(rawPof) || 0;
        const nomThickness = parseFloat(row['Nominal thickness']) || 12.7;

        let type = row['Comments or notes'] || row['Comments or notes to display when clicking + in the table'] || "N/A";

        let severity = "Basso";
        if (pof >= 0.8) severity = "Critico";
        else if (pof >= 0.5) severity = "Alto";
        else if (pof >= 0.2) severity = "Moderato";

        parsedData.push({
            id: `KP-${kp}`,
            position: [lngVal, latVal],
            kp: kp,
            pof: parseFloat(pof.toFixed(3)),
            depth: parseFloat(depth.toFixed(2)),
            nomThickness: nomThickness,
            severity: severity,
            type: String(type)
        });
    }

    return parsedData;
}

function run() {
    const file1 = path.join(__dirname, 'data/BHP_POF_DataExport_ME-BHP-2026-001.xlsx');
    const file2 = path.join(__dirname, 'data/Adjusted records (12.7 mm base).xlsx');
    const file3 = path.join(__dirname, 'data/Adjusted records (12.7 mm base) _1 .xlsx');

    console.log("Parsing Zone 1 - File 1:", file1);
    const data1 = loadAndParse(file1);

    console.log("Parsing Zone 1 - File 2:", file2);
    const data2 = loadAndParse(file2);

    const zone1Data = [...data1, ...data2];

    console.log("Parsing Zone 2 - File 3:", file3);
    const zone2Data = loadAndParse(file3);

    const output = [
        {
            id: "zone1",
            name: "Minera Escondida - Tratto ME-BHP-2026-001",
            data: zone1Data
        },
        {
            id: "zone2",
            name: "Nuova Zona Geografica",
            data: zone2Data
        }
    ];

    const outPath = path.join(__dirname, 'dashboard/public/pipeline_data.json');
    fs.writeFileSync(outPath, JSON.stringify(output, null, 2));

    console.log(`Saved 2 zones to ${outPath}`);
}

run();
