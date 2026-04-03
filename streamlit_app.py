import streamlit as st
import io
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem

# Configure the Streamlit page
st.set_page_config(page_title="StereoChem Explorer", page_icon="🧪", layout="centered")

# Custom CSS for a cooler UI
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #e0c8b0, #ecdac5, #d2b48c) !important;
        color: #5C4033 !important;
    }
    
    /* Sleek buttons */
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background: linear-gradient(90deg, #d4a373, #faedcd) !important;
        color: #5C4033 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(212, 163, 115, 0.4) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(212, 163, 115, 0.6) !important;
    }
    
    /* Text input highlight */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(212, 163, 115, 0.5) !important;
        color: #5C4033 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #d4a373 !important;
        box-shadow: 0 0 10px rgba(212, 163, 115, 0.5) !important;
    }
    
    /* ID Card in Sidebar */
    .id-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.7), rgba(255,255,255,0.4));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(212, 163, 115, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-top: 20px;
        text-align: center;
        color: #5C4033;
    }
    .id-card h3 { margin-bottom: 5px; color: #8c5a2b; font-weight: 700;}
    .id-card p { margin: 8px 0; font-size: 0.95rem; color: #5C4033; }
    .id-name { font-weight: 800; font-size: 1.3rem !important; color: #5C4033 !important; letter-spacing: 1px;}
    
    /* Fix Table and Metric Text Colors */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] > div,
    table, th, td, .stTable, .stDataFrame {
        color: #5C4033 !important;
    }
    
    /* Hide some default elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Custom Main Header
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; margin-top: 20px;">
    <h1 style="background: -webkit-linear-gradient(45deg, #8c5a2b, #d4a373); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 10px;">🧪 StereoChem</h1>
    <p style="font-size: 1.2rem; color: #5C4033; margin-top: -10px; font-weight: 500;">Molecular Stereochemistry Explorer</p>
</div>
""", unsafe_allow_html=True)

# Student Details Sidebar
with st.sidebar:
    st.markdown("""
    <div class="id-card" style="margin-bottom: 15px; padding: 15px;">
        <h3 style="font-size: 1.2rem;">👨‍🎓 User Profile</h3>
        <p style="font-size: 0.85rem; color: #5C4033; margin-top: -5px;">Enter details for report</p>
    </div>
    """, unsafe_allow_html=True)
    
    st_name = st.text_input("Name", value="", placeholder="e.g. John Doe")
    st_regno = st.text_input("Reg No", value="", placeholder="e.g. RA123456789")
    st_class = st.text_input("Class/Sec", value="", placeholder="e.g. AIML-A")
    st_compound = st.text_input("Compound Name", value="", placeholder="e.g. Aspirin")

# Note on public hosting
st.info("💡 **Pro Tip:** This app is fully cloud-native and rendering seamlessly on Streamlit Community Cloud.")

# Input section
smiles_input = st.text_input("Enter SMILES string:", value="", placeholder="e.g. C1CCC(C1)C(C)O")

run_analysis = False
smiles_to_analyze = smiles_input

# Trigger analysis if user types and presses enter
if smiles_input and smiles_input.strip() != "":
    run_analysis = True

if run_analysis and smiles_to_analyze:
    with st.spinner('Analyzing molecule...'):
        try:
            mol = Chem.MolFromSmiles(smiles_to_analyze)
            if mol is None:
                st.error("❌ Failed to load molecule. Please check your SMILES string.")
            else:
                # Add Hydrogens and compute 3D/2D coordinates
                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=42)
                Chem.AssignStereochemistryFrom3D(mol)
                AllChem.Compute2DCoords(mol)
                
                # Find chiral centers
                chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
                
                # Generate Image
                chiral_atoms = [center[0] for center in chiral_centers]
                img = Draw.MolToImage(
                    mol, 
                    highlightAtoms=chiral_atoms,
                    size=(600, 600)
                )
                
                st.markdown("---")
                
                # Display Results Side-by-Side
                col_img, col_data = st.columns([1.5, 1])
                
                with col_img:
                    st.subheader("Molecular Structure")
                    st.image(img, use_container_width=True)
                
                with col_data:
                    st.subheader("Chiral Centers")
                    st.metric(label="Total Stereocenters", value=len(chiral_centers))
                    
                    if chiral_centers:
                        # Format data for Streamlit table
                        formatted_centers = [{"Atom Index": f"Atom {c[0]}", "Configuration": c[1] if c[1] != '?' else 'Unassigned'} for c in chiral_centers]
                        st.table(formatted_centers)
                    else:
                        st.info("No chiral centers found in this molecule.")
                        
                # --- PDF GENERATION ---
                st.markdown("---")
                st.subheader("📥 Download Report")
                
                try:
                    import tempfile
                    import os
                    from fpdf import FPDF
                    
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Title
                    pdf.set_font("helvetica", 'B', 16)
                    pdf.cell(0, 10, "Stereochemistry Analysis Report", new_x="LMARGIN", new_y="NEXT", align='C')
                    pdf.ln(5)
                    
                    # Student Details
                    pdf.set_font("helvetica", 'B', 12)
                    pdf.cell(0, 8, "User Details:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("helvetica", '', 12)
                    pdf.cell(0, 8, f"Name: {st_name}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 8, f"Reg No: {st_regno}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 8, f"Class/Sec: {st_class}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(5)
                    
                    # Compound Details
                    pdf.set_font("helvetica", 'B', 12)
                    pdf.cell(0, 8, "Molecule Details:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("helvetica", '', 12)
                    pdf.cell(0, 8, f"Compound Name: {st_compound}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 8, f"SMILES: {smiles_to_analyze}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(5)
                    
                    # Image
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img.save(tmp.name)
                        pdf.image(tmp.name, x=50, w=110)
                        tmp_path = tmp.name
                    os.unlink(tmp_path)
                    
                    pdf.ln(10)
                    
                    # Chiral Centers
                    pdf.set_font("helvetica", 'B', 12)
                    pdf.cell(0, 8, f"Total Stereocenters: {len(chiral_centers)}", new_x="LMARGIN", new_y="NEXT")
                    
                    if chiral_centers:
                        pdf.set_font("helvetica", 'B', 10)
                        pdf.cell(50, 8, "Atom Index", border=1, align='C')
                        pdf.cell(50, 8, "Configuration", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
                        pdf.set_font("helvetica", '', 10)
                        for center in chiral_centers:
                            idx = f"Atom {center[0]}"
                            cfg = center[1] if center[1] != '?' else 'Unassigned'
                            pdf.cell(50, 8, idx, border=1, align='C')
                            pdf.cell(50, 8, cfg, border=1, new_x="LMARGIN", new_y="NEXT", align='C')
                    else:
                        pdf.set_font("helvetica", '', 12)
                        pdf.cell(0, 8, "No chiral centers found in this molecule.", new_x="LMARGIN", new_y="NEXT")
                        
                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{st_compound.replace(' ', '_') if st_compound else 'Molecule'}_Report.pdf",
                        mime="application/pdf"
                    )
                except Exception as pdf_e:
                    st.error(f"Couldn't generate PDF: {str(pdf_e)}")
                        
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
