#!/usr/bin/env python3
"""
Script to create a sample PDF for testing the PDF Chat Appliance ingestion workflow.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

def create_sample_pdf():
    """Create a sample PDF with company overview and technical content."""
    
    # Create documents directory if it doesn't exist
    os.makedirs("documents", exist_ok=True)
    
    # Create the PDF document
    doc = SimpleDocTemplate("documents/sample-doc.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Content for the PDF
    story = []
    
    # Title
    story.append(Paragraph("TechCorp Solutions - Network Security Overview", title_style))
    story.append(Spacer(1, 20))
    
    # Company Overview
    story.append(Paragraph("Company Overview", heading_style))
    story.append(Paragraph(
        "TechCorp Solutions is a leading cybersecurity company founded in 2018, specializing in "
        "enterprise network security and compliance solutions. Our mission is to provide "
        "comprehensive security infrastructure that protects organizations from evolving cyber threats "
        "while maintaining operational efficiency and regulatory compliance.",
        normal_style
    ))
    story.append(Paragraph(
        "The company serves over 500 enterprise clients across healthcare, finance, and government "
        "sectors, with annual revenue exceeding $50 million. Our headquarters is located in "
        "San Francisco, California, with regional offices in New York, London, and Singapore.",
        normal_style
    ))
    
    # Network Architecture
    story.append(Paragraph("Network Architecture & Infrastructure", heading_style))
    story.append(Paragraph(
        "Our core network infrastructure utilizes a multi-layered security approach with the "
        "following key components:",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Firewall Configuration:</b> We deploy Palo Alto Networks PA-5220 next-generation "
        "firewalls at all perimeter points, configured with application-aware policies and "
        "threat prevention capabilities.",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Intrusion Detection System:</b> Snort IDS sensors are strategically placed throughout "
        "the network to monitor traffic patterns and detect potential security breaches.",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Load Balancers:</b> F5 BIG-IP load balancers distribute traffic across redundant "
        "application servers while providing SSL termination and DDoS protection.",
        normal_style
    ))
    
    # Security Policies
    story.append(Paragraph("Security Policies & Compliance", heading_style))
    story.append(Paragraph(
        "TechCorp maintains strict security policies aligned with industry standards including "
        "ISO 27001, SOC 2 Type II, and NIST Cybersecurity Framework. Our security program "
        "encompasses:",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Access Control:</b> Multi-factor authentication (MFA) is mandatory for all system "
        "access, with role-based access control (RBAC) implemented across all platforms.",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Data Protection:</b> All sensitive data is encrypted at rest using AES-256 encryption "
        "and in transit using TLS 1.3 protocols.",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Incident Response:</b> Our Security Operations Center (SOC) operates 24/7 with "
        "automated threat detection and response capabilities.",
        normal_style
    ))
    
    # Technical Specifications
    story.append(Paragraph("Technical Specifications", heading_style))
    story.append(Paragraph(
        "The primary firewall used in our infrastructure is the Palo Alto Networks PA-5220, "
        "which provides advanced threat prevention, URL filtering, and application control. "
        "This firewall is configured with the following specifications:",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Throughput:</b> 20 Gbps firewall throughput with 4 Gbps threat prevention",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Connections:</b> Support for up to 2 million concurrent connections",
        normal_style
    ))
    story.append(Paragraph(
        "• <b>Features:</b> Advanced malware protection, SSL decryption, and user identification",
        normal_style
    ))
    
    # Business Goals
    story.append(Paragraph("Business Objectives & Goals", heading_style))
    story.append(Paragraph(
        "The main goal of this document is to provide a comprehensive overview of TechCorp's "
        "network security infrastructure and demonstrate our commitment to protecting client "
        "data and maintaining regulatory compliance. Our primary objectives include:",
        normal_style
    ))
    story.append(Paragraph(
        "• Ensuring 99.9% uptime for all critical systems",
        normal_style
    ))
    story.append(Paragraph(
        "• Maintaining compliance with all applicable regulations",
        normal_style
    ))
    story.append(Paragraph(
        "• Providing real-time threat detection and response",
        normal_style
    ))
    story.append(Paragraph(
        "• Supporting business growth while maintaining security posture",
        normal_style
    ))
    
    # Build the PDF
    doc.build(story)
    print("✅ Sample PDF created: documents/sample-doc.pdf")

if __name__ == "__main__":
    create_sample_pdf() 