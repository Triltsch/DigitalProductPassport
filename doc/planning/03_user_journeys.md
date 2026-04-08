# 03 — User Journeys

## Overview

This document describes the primary use cases and user flows for each stakeholder role. Each journey is specified at a level suitable for deriving UI wireframes, API endpoint contracts, and domain event definitions.

---

## 1. Manufacturer Journeys

### UC-M-01: Create a New Digital Product Passport

**Actor:** Manufacturer  
**Precondition:** User is authenticated with `MANUFACTURER` role; organization (tenant) is set up.  
**Goal:** Create a complete DPP for a new product.

**Flow:**
1. Manufacturer navigates to "My Products" dashboard → clicks "Create New Passport".
2. Enters basic product information: product name, model number, category, manufacturer details.
3. System generates a globally unique `assetId` (URI) for the product.
4. System creates an AAS shell in `DRAFT` state with an empty Technical Data submodel.
5. Manufacturer fills in submodel data step-by-step:
   - Technical Data (dimensions, materials, components)
   - Sustainability (carbon footprint, recyclability)
   - Provenance (supply chain origin, material certificates)
   - Certifications (upload certificate documents, link to issuer)
6. System validates each submodel against the corresponding IDTA Submodel Template.
7. Manufacturer reviews a summary view of the complete DPP.
8. Manufacturer clicks "Publish" → DPP transitions to `ACTIVE` state.
9. System generates a shareable DPP link and QR code.

**Exceptions:**
- Validation fails: user is shown field-level errors; DPP remains in `DRAFT`.
- Required submodel fields are missing: user cannot publish until all mandatory fields are provided.

---

### UC-M-02: Update an Existing DPP

**Actor:** Manufacturer  
**Precondition:** DPP exists in `ACTIVE` state.

**Flow:**
1. Manufacturer selects DPP from dashboard → clicks "Edit".
2. System creates a new draft version of the DPP linked to the original.
3. Manufacturer modifies submodel data.
4. Manufacturer publishes the new version; previous version is archived.
5. Access grants from previous version are inherited by the new version.

---

### UC-M-03: Grant Access to a Supplier

**Actor:** Manufacturer  
**Precondition:** DPP exists. Supplier user exists in the system.

**Flow:**
1. Manufacturer opens DPP → navigates to "Access Management".
2. Manufacturer searches for supplier by email or organization name.
3. Manufacturer selects the scope of access: specific submodels and/or write permissions.
4. System sends an access notification to the supplier.
5. Supplier can now access the designated submodels.

---

### UC-M-04: Submit DPP for Certification

**Actor:** Manufacturer  
**Precondition:** DPP is in `ACTIVE` state. At least one Certification Body (Auditor) exists in the system.

**Flow:**
1. Manufacturer opens DPP → clicks "Request Certification".
2. Selects certification body and certification type (e.g., "ISO 14001 Environmental Audit").
3. Optionally attaches supporting documents.
4. System creates a certification workflow record in `PENDING_REVIEW` state.
5. Auditor is notified.

---

## 2. Supplier Journeys

### UC-S-01: Submit Component Data to a DPP

**Actor:** Supplier  
**Precondition:** Supplier has received an access grant to a Provenance or Technical Data submodel.

**Flow:**
1. Supplier logs in → sees "Access Requests" notifications on dashboard.
2. Supplier opens the corresponding product DPP.
3. Supplier navigates to the submodel they are authorized to contribute to.
4. Supplier fills in material/component details and origin information.
5. System validates the input and saves it as a pending change.
6. Manufacturer receives a notification for review (if supplier has `WRITE_PENDING_APPROVAL` scope).
7. Manufacturer approves or rejects the supplier's contribution.

---

### UC-S-02: View a Shared DPP

**Actor:** Supplier  
**Precondition:** Supplier has read access to one or more submodels of a DPP.

**Flow:**
1. Supplier navigates to "Shared with Me" section.
2. Supplier opens the product DPP.
3. Views only the submodels they are authorized to see.
4. Can download authorized submodel data in JSON or AASX format.

---

## 3. Auditor Journeys

### UC-A-01: Conduct a Certification Review

**Actor:** Auditor  
**Precondition:** An open certification request exists in `PENDING_REVIEW` state.

**Flow:**
1. Auditor logs in → sees open review tasks on dashboard.
2. Auditor opens the assigned DPP certification request.
3. System presents the full DPP data (read-only view) including all submodels.
4. Auditor reviews each relevant submodel and attached documents.
5. Auditor adds structured audit findings (pass/fail per criteria, comments).
6. Auditor makes a final decision:
   - **Approve:** workflow transitions to `APPROVED`; system attaches a certificate record to the DPP.
   - **Request Changes:** workflow transitions to `CHANGES_REQUESTED`; manufacturer is notified with comments.
   - **Reject:** workflow transitions to `REJECTED`; manufacturer is notified with reasons.
7. If approved, a certificate is digitally signed and stored in the Certifications submodel.

---

### UC-A-02: Issue an Independent Certificate

**Actor:** Auditor  
**Precondition:** Auditor has direct access to the DPP (not via formal workflow).

**Flow:**
1. Auditor opens DPP via direct link or search.
2. Navigates to "Certifications" submodel.
3. Clicks "Issue Certificate" → fills in certificate details (standard, scope, validity period).
4. Uploads signed certificate document.
5. System creates a certificate record linked to the DPP.

---

## 4. Customer Journeys

### UC-C-01: View a Public Product Passport

**Actor:** End Customer (unauthenticated or authenticated)  
**Precondition:** DPP is `ACTIVE` and has at least some publicly disclosed fields.

**Flow:**
1. Customer scans QR code on physical product or follows a shared URL.
2. System displays the public DPP view (no login required for public data).
3. Customer sees:
   - Product name, category, manufacturer
   - Sustainability summary (carbon footprint tier, recycled content %)
   - Active certifications
   - Repair/end-of-life guidance
4. Customer may click "Request Full Access" to create an account and request additional data disclosure from the manufacturer.

---

## 5. Regulator Journeys

### UC-R-01: Access Compliance Data for a Product

**Actor:** Regulator  
**Precondition:** Regulator has been granted access by the manufacturer or platform admin.

**Flow:**
1. Regulator logs in → views accessible products.
2. Filters products by category, certification status, or date range.
3. Opens a specific DPP → views compliance-relevant submodels (Sustainability, Certifications).
4. Downloads a structured regulatory export (JSON-LD, CSV) for submission to regulatory authority.

---

## 6. Cross-Role Journeys

### UC-X-01: End-to-End Lifecycle Event Recording

**Actors:** Manufacturer, Supplier, Auditor  
**Goal:** Track product lifecycle events across all stages.

**Flow:**
1. **Manufacturing event:** Manufacturer records "Product assembled" lifecycle event with timestamp and facility data.
2. **Shipment event:** Supplier records "Shipped to distributor" with logistics reference.
3. **Inspection event:** Auditor records "Compliance inspection passed" with certificate reference.
4. **Customer event:** Customer scans product and logs "First use" (if feature is enabled).
5. **End-of-life event:** Recycler records "Disassembly started" with material recovery data.

All events are append-only, timestamped, and visible in the DPP event timeline.

---

### UC-X-02: AAS Bulk Import from AASX File

**Actors:** Manufacturer, System Administrator  
**Goal:** Onboard a large product catalog efficiently.

**Flow:**
1. User navigates to "Import" section.
2. Uploads one or more `.aasx` files.
3. System parses the AASX packages and validates each AAS and submodel.
4. System displays a preview of imported assets with validation results.
5. User confirms import → AAS instances are created in `DRAFT` state.
6. User reviews and publishes individual or all imported passports.

---

## 7. Admin Journeys

### UC-AD-01: Onboard a New Organization (Tenant)

**Actor:** System Administrator  
**Flow:**
1. Admin creates a new tenant with organization details.
2. Admin creates the initial `MANUFACTURER` user account.
3. Admin assigns Keycloak realm roles.
4. New user receives an invitation email and sets their password.
5. Tenant is active and can begin creating DPPs.
