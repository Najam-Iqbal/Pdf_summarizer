
import os
import fitz
import nltk
import streamlit as st

import PyPDF2
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, PageBreak
from xml.sax.saxutils import escape

# ... (rest of the code remains the same)

def generate_pdf(output_path, pages):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom paragraph style for summaries
    summary_style = ParagraphStyle(
        name="SummaryStyle",
        fontSize=12,
        fontName="Helvetica-Bold",
        leading=18,
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=0,
        rightIndent=0,
        alignment=1  # Align left
    )

    flowables = []
    for page_content in pages:
        # Add summary paragraph with proper indentation
        summary_paragraph = Paragraph(page_content['summary'], style=summary_style)
        summary_paragraph.indent = 18  # Adjust indentation as needed
        flowables.append(summary_paragraph)

        # Create table for key terms and meanings
        data = [["Term", "Meaning"]]  # Header row
        for term, meaning in page_content['meanings'].items():
            data.append([term, meaning])

        # Define table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text left
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), (1, 1, 1)),  # Alternate row background
            ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Grid lines
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Vertical alignment
        ])

        # Define column widths and create table
        col_widths = [2.5*inch, 4.5*inch]  # Adjust column widths as needed
        table = Table(data, colWidths=col_widths)
        table.setStyle(table_style)

        # Add table to flowables with proper indentation
        table.hAlign = 'LEFT'
        table.leftIndent = 18  # Adjust indentation as needed
        flowables.append(table)

        # Add page break after each page's content
        flowables.append(PageBreak())

    # Build the PDF
    doc.build(flowables)

def main():
    st.title("PDF Summarizer and Key Term Extractor")

    # PDF File Upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        st.write("Processing...")
        pdf_path = "temp_uploaded.pdf"

        # Save the uploaded file temporarily
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text from PDF
        texts = extract_text_from_pdf(pdf_path)

        use_llama = st.checkbox("Use LLaMA for Key Term Extraction", value=True)
        top_n_terms = st.slider("Number of Key Terms to Extract", min_value=1, max_value=20, value=10)

        pages = []
        for idx, text in enumerate(texts[:10], 1):  # Limit to first 10 pages
            summary, meanings = process_text(text, use_llama=use_llama, top_n=top_n_terms)
            page_content = {
                'summary': f"**Page {idx} Summary:**\n{summary}",
                'meanings': meanings
            }
            pages.append(page_content)

        # Output PDF file
        output_pdf_path = "output_summary.pdf"
        generate_pdf(output_pdf_path, pages)

        st.success("PDF generation complete! Download your file below.")
        with open(output_pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name=output_pdf_path)

if __name__ == "__main__":
    main()
