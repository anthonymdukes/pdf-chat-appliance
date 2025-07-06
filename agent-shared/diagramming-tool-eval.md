# Diagramming Tool Evaluation & Selection

**Date:** 2025-07-06  
**Initiative:** Visual Architecture Deployment  
**Status:** Tool Evaluation & Selection  
**Participants:** system-architect, docs-maintainer, observability-agent, qa-tester

---

## Executive Summary

This document evaluates and selects a local, containerized diagramming tool for architecture visualization, org structure mapping, and future sprint documentation. The evaluation focuses on Docker Desktop compatibility, local operation, output formats, and ease of use.

**Selected Tool:** `fjudith/drawio` (Draw.io Desktop)

---

## Tool Evaluation Criteria

### ✅ **Required Criteria**
- **Docker Desktop Compatibility:** Must run inside Docker Desktop
- **Local Operation:** No internet access or user login required
- **Output Formats:** Support for `.png`, `.svg`, `.mmd`, or `.drawio` files
- **Mount Integration:** Use existing mount (`agent-shared/diagrams/`)
- **Stability:** Reliable and well-maintained

### 🎯 **Desired Criteria**
- **Ease of Use:** Intuitive interface for architecture diagrams
- **Feature Richness:** Support for complex diagrams and flows
- **Export Capabilities:** Multiple output formats
- **Performance:** Fast loading and responsive
- **Community Support:** Active development and community

---

## Tool Evaluation Matrix

### 1. **fjudith/drawio** (Draw.io Desktop)

#### **Technical Assessment**
- **Docker Compatibility:** ✅ Excellent - Official Docker image
- **Local Operation:** ✅ Full offline capability
- **Output Formats:** ✅ `.png`, `.svg`, `.drawio`, `.xml`
- **Mount Integration:** ✅ Supports volume mounting
- **Stability:** ✅ Very stable, widely used

#### **Feature Assessment**
- **Architecture Diagrams:** ✅ Excellent - Built for technical diagrams
- **Org Charts:** ✅ Excellent - Organizational structure support
- **Flow Diagrams:** ✅ Excellent - Process and data flow support
- **Collaboration:** ✅ Good - File-based sharing
- **Templates:** ✅ Excellent - Rich template library

#### **Performance Assessment**
- **Loading Speed:** ✅ Fast - Lightweight container
- **Responsiveness:** ✅ Excellent - Web-based interface
- **Resource Usage:** ✅ Low - Minimal resource requirements
- **Scalability:** ✅ Good - Handles complex diagrams

#### **Community Assessment**
- **Active Development:** ✅ Very active - Regular updates
- **Documentation:** ✅ Excellent - Comprehensive docs
- **Community Support:** ✅ Large community - Extensive resources
- **License:** ✅ Open source - Apache 2.0

#### **Pros:**
- Industry standard for technical diagrams
- Excellent architecture diagram capabilities
- Rich template library
- Full offline operation
- Multiple export formats
- Active development and community

#### **Cons:**
- Web-based interface (may be unfamiliar to some)
- Learning curve for advanced features
- File format is proprietary (though exportable)

### 2. **jgraph/docker-drawio** (Alternative Draw.io)

#### **Technical Assessment**
- **Docker Compatibility:** ✅ Good - Docker image available
- **Local Operation:** ✅ Full offline capability
- **Output Formats:** ✅ `.png`, `.svg`, `.drawio`, `.xml`
- **Mount Integration:** ✅ Supports volume mounting
- **Stability:** ✅ Stable - Based on draw.io

#### **Feature Assessment**
- **Architecture Diagrams:** ✅ Good - Same as fjudith/drawio
- **Org Charts:** ✅ Good - Organizational structure support
- **Flow Diagrams:** ✅ Good - Process and data flow support
- **Collaboration:** ✅ Good - File-based sharing
- **Templates:** ✅ Good - Template library available

#### **Performance Assessment**
- **Loading Speed:** ✅ Good - Similar to fjudith/drawio
- **Responsiveness:** ✅ Good - Web-based interface
- **Resource Usage:** ✅ Low - Minimal resource requirements
- **Scalability:** ✅ Good - Handles complex diagrams

#### **Community Assessment**
- **Active Development:** ⚠️ Moderate - Less active than fjudith
- **Documentation:** ✅ Good - Adequate documentation
- **Community Support:** ⚠️ Moderate - Smaller community
- **License:** ✅ Open source - Apache 2.0

#### **Pros:**
- Based on draw.io (proven technology)
- Full offline operation
- Multiple export formats
- Good architecture diagram support

#### **Cons:**
- Less active development
- Smaller community
- Same learning curve as draw.io
- No significant advantages over fjudith/drawio

### 3. **Mermaid Live Editor Container**

#### **Technical Assessment**
- **Docker Compatibility:** ⚠️ Limited - No official container
- **Local Operation:** ✅ Full offline capability
- **Output Formats:** ✅ `.png`, `.svg`, `.mmd`
- **Mount Integration:** ⚠️ Complex - Requires custom setup
- **Stability:** ⚠️ Moderate - Community containers only

#### **Feature Assessment**
- **Architecture Diagrams:** ✅ Good - Text-based diagramming
- **Org Charts:** ✅ Good - Organizational structure support
- **Flow Diagrams:** ✅ Excellent - Process and data flow support
- **Collaboration:** ✅ Good - Text-based sharing
- **Templates:** ⚠️ Limited - Fewer templates

#### **Performance Assessment**
- **Loading Speed:** ✅ Fast - Lightweight
- **Responsiveness:** ✅ Good - Text-based interface
- **Resource Usage:** ✅ Very low - Minimal resources
- **Scalability:** ✅ Excellent - Handles complex diagrams

#### **Community Assessment**
- **Active Development:** ✅ Very active - Regular updates
- **Documentation:** ✅ Excellent - Comprehensive docs
- **Community Support:** ✅ Large community - Extensive resources
- **License:** ✅ Open source - MIT

#### **Pros:**
- Text-based diagramming (version control friendly)
- Excellent for flow diagrams
- Very lightweight
- Active development
- Markdown integration

#### **Cons:**
- No official Docker container
- Complex setup for local operation
- Limited visual design capabilities
- Steeper learning curve for complex diagrams

### 4. **PlantUML Container**

#### **Technical Assessment**
- **Docker Compatibility:** ✅ Good - Official Docker image
- **Local Operation:** ✅ Full offline capability
- **Output Formats:** ✅ `.png`, `.svg`, `.puml`
- **Mount Integration:** ✅ Supports volume mounting
- **Stability:** ✅ Very stable - Mature tool

#### **Feature Assessment**
- **Architecture Diagrams:** ✅ Excellent - Built for UML
- **Org Charts:** ⚠️ Limited - Not primary focus
- **Flow Diagrams:** ✅ Excellent - Sequence and activity diagrams
- **Collaboration:** ✅ Good - Text-based sharing
- **Templates:** ✅ Good - UML templates

#### **Performance Assessment**
- **Loading Speed:** ✅ Fast - Command-line tool
- **Responsiveness:** ✅ Excellent - Fast processing
- **Resource Usage:** ✅ Low - Minimal resources
- **Scalability:** ✅ Excellent - Handles complex diagrams

#### **Community Assessment**
- **Active Development:** ✅ Active - Regular updates
- **Documentation:** ✅ Excellent - Comprehensive docs
- **Community Support:** ✅ Large community - Extensive resources
- **License:** ✅ Open source - GPL

#### **Pros:**
- Excellent for UML diagrams
- Text-based (version control friendly)
- Very fast processing
- Mature and stable
- Active development

#### **Cons:**
- Focused on UML (less flexible for org charts)
- Steeper learning curve
- Limited visual design capabilities
- Not ideal for organizational diagrams

---

## Redeployment & Port Conflict Resolution (2025-07-06)

- **Issue:** Draw.io and Open WebUI both used port 8080, causing a conflict.
- **Action:** Stopped and removed the original Draw.io container.
- **Redeployed Draw.io** on port **8081** using:
  ```sh
  docker run -d --name drawio -p 8081:8080 -v ${PWD}/agent-shared/diagrams:/opt/drawio/diagrams jgraph/drawio:latest
  ```
- **Result:**
  - Draw.io is now accessible at [http://localhost:8081](http://localhost:8081)
  - No conflict with Open WebUI or other services
  - Port registry (`agent-shared/ports.md`) and documentation updated
- **Test:** Service verified operational via curl and browser access
- **Status:** ✅ Conflict resolved, Draw.io fully functional on new port

---

## Tool Selection Decision

### 🏆 **Selected Tool: fjudith/drawio**

#### **Selection Rationale**

**Primary Factors:**
1. **Best Architecture Diagram Support:** Draw.io is the industry standard for technical architecture diagrams
2. **Excellent Org Chart Capabilities:** Perfect for enterprise agent reorganization visualization
3. **Rich Template Library:** Extensive templates for various diagram types
4. **Full Offline Operation:** No internet access required
5. **Multiple Export Formats:** Supports all required output formats
6. **Active Development:** Regular updates and community support

**Secondary Factors:**
1. **Ease of Use:** Intuitive web-based interface
2. **Performance:** Fast loading and responsive
3. **Stability:** Very stable and widely used
4. **Community Support:** Large community and extensive resources

#### **Alternative Consideration: Mermaid**

**Why Not Mermaid:**
- **Setup Complexity:** No official Docker container, complex local setup
- **Limited Visual Design:** Text-based approach limits visual creativity
- **Learning Curve:** Steeper learning curve for complex diagrams
- **Org Chart Limitations:** Less suitable for organizational diagrams

**Mermaid Integration:**
- **Future Consideration:** May integrate Mermaid for specific flow diagrams
- **Hybrid Approach:** Use Draw.io for architecture/org charts, Mermaid for flows
- **Markdown Integration:** Mermaid can be embedded in documentation

---

## Implementation Plan

### 🚀 **Phase 1: Tool Deployment (Immediate)**

#### **Docker Container Setup**
```bash
# Create diagrams directory
mkdir -p agent-shared/diagrams

# Deploy Draw.io container
docker run -d \
  --name drawio \
  -p 8080:8080 \
  -v $(pwd)/agent-shared/diagrams:/opt/drawio/diagrams \
  fjudith/drawio:latest
```

#### **Configuration**
- **Port:** 8080 (local access)
- **Mount:** `agent-shared/diagrams/` for file persistence
- **Access:** `http://localhost:8080`
- **Storage:** Local file system integration

### 🎯 **Phase 2: Diagram Creation (Short-term)**

#### **PDF Chat Appliance Architecture**
- **File:** `agent-shared/diagrams/pdf-chat-architecture.drawio`
- **Exports:** `.png`, `.svg` for documentation
- **Components:** Ingestion pipeline, embedding, vector DB, query path, LLM routing

#### **Enterprise Agent Reorganization**
- **File:** `agent-shared/diagrams/org-chart.drawio`
- **Exports:** `.png`, `.svg` for documentation
- **Components:** Agent-core, divisions, shared-services, orchestration flows

### 📊 **Phase 3: Documentation Integration (Medium-term)**

#### **Documentation Updates**
- **`docs/ROOT_ARCHITECTURE.md`:** Embed PDF Chat Appliance diagrams
- **`docs/TEAM_STRUCTURE.md`:** Embed Enterprise Agent Reorganization diagrams
- **`agent-shared/README.md`:** Add diagram references and navigation

#### **Template Creation**
- **Architecture Templates:** Standardized templates for future diagrams
- **Org Chart Templates:** Templates for team structure visualization
- **Flow Templates:** Templates for process and data flow diagrams

---

## Success Metrics

### 📊 **Deployment Metrics**
- **Container Stability:** 99%+ uptime
- **File Persistence:** 100% file persistence across container restarts
- **Performance:** <2 second loading time
- **Accessibility:** 100% local access without internet

### 🎯 **Diagram Quality Metrics**
- **Architecture Clarity:** Clear visualization of system components
- **Org Structure Clarity:** Clear visualization of team structure
- **Export Quality:** High-quality exports for documentation
- **Template Usage:** Effective use of templates for consistency

### 📈 **Usage Metrics**
- **Diagram Creation:** 2+ high-quality diagrams created
- **Documentation Integration:** Diagrams embedded in documentation
- **Template Adoption:** Templates used for future diagrams
- **Team Adoption:** Team members using the tool effectively

---

## Risk Assessment

### 🟢 **Low Risk**
- **Tool Stability:** Draw.io is very stable and widely used
- **Docker Compatibility:** Official Docker image with good support
- **File Persistence:** Volume mounting ensures file persistence
- **Community Support:** Large community for troubleshooting

### 🟡 **Medium Risk**
- **Learning Curve:** Team may need time to learn advanced features
- **File Format:** Proprietary format (mitigated by export capabilities)
- **Performance:** Complex diagrams may impact performance
- **Integration:** Documentation integration may require adjustments

### 🔴 **High Risk**
- **None Identified:** Tool selection and deployment are low-risk

---

## Conclusion

### ✅ **Tool Selection: CONFIRMED**

**Selected Tool:** `fjudith/drawio` (Draw.io Desktop)

**Rationale:**
- Best architecture diagram capabilities
- Excellent org chart support
- Rich template library
- Full offline operation
- Active development and community
- Industry standard for technical diagrams

### 🚀 **Implementation Readiness: HIGH**

**Ready for:**
- Immediate Docker container deployment
- Architecture diagram creation
- Org structure visualization
- Documentation integration

**Next Steps:**
1. **Immediate:** Deploy Draw.io container
2. **Short-term:** Create PDF Chat Appliance architecture diagram
3. **Short-term:** Create Enterprise Agent Reorganization diagram
4. **Medium-term:** Integrate diagrams into documentation

### 📋 **Success Criteria**

**Deployment Success:**
- Container running on localhost:8080
- File persistence working correctly
- No internet access required
- Fast and responsive interface

**Diagram Success:**
- Clear architecture visualization
- Clear org structure visualization
- High-quality exports
- Documentation integration

**Ready for immediate implementation.**

---

**Evaluation Complete:** 2025-07-06  
**Next Review:** Post-deployment validation  
**Status:** Ready for Implementation 