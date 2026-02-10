const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
        TableOfContents, LevelFormat, PageBreak } = require('docx');
const fs = require('fs');

/**
 * Generates a professional requirements document from JSON structure
 * @param {Object} reqData - Requirements data from AI agent
 * @param {string} outputPath - Path to save the .docx file
 */
async function generateRequirementsDoc(reqData, outputPath) {
    const sections = [];

    // Helper function to create bullet list paragraphs
    function createBulletList(items, reference = "bullets") {
        return items.map(item => 
            new Paragraph({
                numbering: { reference, level: 0 },
                children: [new TextRun(item)]
            })
        );
    }

    // Helper function to create numbered list paragraphs
    function createNumberedList(items, reference = "numbers") {
        return items.map((item, index) => 
            new Paragraph({
                numbering: { reference, level: 0 },
                children: [new TextRun(item)]
            })
        );
    }

    // Title Page
    sections.push(
        new Paragraph({
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            children: [new TextRun({ text: reqData.projectName || "Legacy Application Modernization", bold: true, size: 48 })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            children: [new TextRun({ text: "Requirements Document", size: 32 })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `Generated: ${new Date().toLocaleDateString()}`, size: 24 })]
        }),
        new Paragraph({ children: [new PageBreak()] })
    );

    // Table of Contents
    sections.push(
        new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [new TextRun("Table of Contents")]
        }),
        new TableOfContents("Table of Contents", {
            hyperlink: true,
            headingStyleRange: "1-3"
        }),
        new Paragraph({ children: [new PageBreak()] })
    );

    // Executive Summary
    sections.push(
        new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [new TextRun("1. Executive Summary")]
        }),
        new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun(reqData.executiveSummary || "")]
        })
    );

    // Business Context
    if (reqData.businessContext) {
        sections.push(
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("2. Business Context")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("2.1 Purpose")]
            }),
            new Paragraph({
                children: [new TextRun(reqData.businessContext.purpose || "")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("2.2 Target Users")]
            }),
            ...createBulletList(reqData.businessContext.users || []),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("2.3 Key Functions")]
            }),
            ...createBulletList(reqData.businessContext.keyFunctions || [])
        );
    }

    // Functional Requirements
    if (reqData.functionalRequirements && reqData.functionalRequirements.length > 0) {
        sections.push(
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("3. Functional Requirements")]
            })
        );

        // Create requirements table
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        
        const reqRows = [
            // Header row
            new TableRow({
                children: [
                    new TableCell({
                        borders,
                        width: { size: 1500, type: WidthType.DXA },
                        shading: { fill: "4472C4", type: ShadingType.CLEAR },
                        children: [new Paragraph({ children: [new TextRun({ text: "ID", bold: true, color: "FFFFFF" })] })]
                    }),
                    new TableCell({
                        borders,
                        width: { size: 2000, type: WidthType.DXA },
                        shading: { fill: "4472C4", type: ShadingType.CLEAR },
                        children: [new Paragraph({ children: [new TextRun({ text: "Category", bold: true, color: "FFFFFF" })] })]
                    }),
                    new TableCell({
                        borders,
                        width: { size: 5860, type: WidthType.DXA },
                        shading: { fill: "4472C4", type: ShadingType.CLEAR },
                        children: [new Paragraph({ children: [new TextRun({ text: "Requirement", bold: true, color: "FFFFFF" })] })]
                    })
                ]
            })
        ];

        // Data rows
        reqData.functionalRequirements.forEach(req => {
            reqRows.push(
                new TableRow({
                    children: [
                        new TableCell({
                            borders,
                            width: { size: 1500, type: WidthType.DXA },
                            children: [new Paragraph({ children: [new TextRun(req.id)] })]
                        }),
                        new TableCell({
                            borders,
                            width: { size: 2000, type: WidthType.DXA },
                            children: [new Paragraph({ children: [new TextRun(req.category)] })]
                        }),
                        new TableCell({
                            borders,
                            width: { size: 5860, type: WidthType.DXA },
                            children: [
                                new Paragraph({ children: [new TextRun({ text: req.title, bold: true })] }),
                                new Paragraph({ children: [new TextRun(req.description)] }),
                                new Paragraph({ children: [new TextRun({ text: `Priority: ${req.priority}`, italics: true })] })
                            ]
                        })
                    ]
                })
            );
        });

        sections.push(
            new Table({
                width: { size: 9360, type: WidthType.DXA },
                columnWidths: [1500, 2000, 5860],
                rows: reqRows
            })
        );
    }

    // Data Requirements
    if (reqData.dataRequirements && reqData.dataRequirements.entities) {
        sections.push(
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("4. Data Requirements")]
            })
        );

        reqData.dataRequirements.entities.forEach((entity, index) => {
            sections.push(
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun(`4.${index + 1} ${entity.name}`)]
                }),
                new Paragraph({
                    children: [new TextRun(entity.description)]
                }),
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun("Attributes:")]
                })
            );

            // Attributes table
            const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
            const borders = { top: border, bottom: border, left: border, right: border };
            
            const attrRows = [
                new TableRow({
                    children: [
                        new TableCell({
                            borders,
                            width: { size: 2340, type: WidthType.DXA },
                            shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                            children: [new Paragraph({ children: [new TextRun({ text: "Name", bold: true })] })]
                        }),
                        new TableCell({
                            borders,
                            width: { size: 2340, type: WidthType.DXA },
                            shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                            children: [new Paragraph({ children: [new TextRun({ text: "Type", bold: true })] })]
                        }),
                        new TableCell({
                            borders,
                            width: { size: 4680, type: WidthType.DXA },
                            shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                            children: [new Paragraph({ children: [new TextRun({ text: "Description", bold: true })] })]
                        })
                    ]
                })
            ];

            entity.attributes.forEach(attr => {
                attrRows.push(
                    new TableRow({
                        children: [
                            new TableCell({
                                borders,
                                width: { size: 2340, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun(attr.name + (attr.required ? " *" : ""))] })]
                            }),
                            new TableCell({
                                borders,
                                width: { size: 2340, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun(attr.type)] })]
                            }),
                            new TableCell({
                                borders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun(attr.description || "")] })]
                            })
                        ]
                    })
                );
            });

            sections.push(
                new Table({
                    width: { size: 9360, type: WidthType.DXA },
                    columnWidths: [2340, 2340, 4680],
                    rows: attrRows
                })
            );
        });
    }

    // Business Rules
    if (reqData.businessRules && reqData.businessRules.length > 0) {
        sections.push(
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("5. Business Rules")]
            })
        );

        reqData.businessRules.forEach((rule, index) => {
            sections.push(
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun(`5.${index + 1} ${rule.rule}`)]
                }),
                new Paragraph({
                    children: [new TextRun({ text: "Implementation: ", bold: true }), new TextRun(rule.implementation)]
                }),
                new Paragraph({
                    children: [new TextRun({ text: "Validations:", bold: true })]
                }),
                ...createBulletList(rule.validations || [])
            );
        });
    }

    // Create the document
    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: { font: "Arial", size: 24 }
                }
            },
            paragraphStyles: [
                {
                    id: "Heading1",
                    name: "Heading 1",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 32, bold: true, font: "Arial", color: "2F5496" },
                    paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
                },
                {
                    id: "Heading2",
                    name: "Heading 2",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 28, bold: true, font: "Arial", color: "2F5496" },
                    paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 }
                },
                {
                    id: "Heading3",
                    name: "Heading 3",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 26, bold: true, font: "Arial", color: "1F3864" },
                    paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 }
                }
            ]
        },
        numbering: {
            config: [
                {
                    reference: "bullets",
                    levels: [
                        {
                            level: 0,
                            format: LevelFormat.BULLET,
                            text: "•",
                            alignment: AlignmentType.LEFT,
                            style: {
                                paragraph: {
                                    indent: { left: 720, hanging: 360 }
                                }
                            }
                        }
                    ]
                },
                {
                    reference: "numbers",
                    levels: [
                        {
                            level: 0,
                            format: LevelFormat.DECIMAL,
                            text: "%1.",
                            alignment: AlignmentType.LEFT,
                            style: {
                                paragraph: {
                                    indent: { left: 720, hanging: 360 }
                                }
                            }
                        }
                    ]
                }
            ]
        },
        sections: [{
            properties: {
                page: {
                    size: {
                        width: 12240,  // US Letter width
                        height: 15840  // US Letter height
                    },
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                }
            },
            children: sections
        }]
    });

    // Generate and save
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
    console.log(`Requirements document generated: ${outputPath}`);
    return outputPath;
}

module.exports = { generateRequirementsDoc };

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.log("Usage: node generate_requirements_doc.js <input_json> <output_docx>");
        process.exit(1);
    }

    const reqData = JSON.parse(fs.readFileSync(args[0], 'utf8'));
    generateRequirementsDoc(reqData, args[1])
        .then(() => console.log("Done!"))
        .catch(err => console.error("Error:", err));
}
