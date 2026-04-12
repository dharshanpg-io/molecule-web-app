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
        background: linear-gradient(135deg, #e6d3c1, #f2e3d5, #d9be9e) !important;
        background-attachment: fixed !important;
    }
    
    /* Glassmorphism Main Container */
    .block-container {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 40px rgba(92, 64, 51, 0.15) !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 800px !important;
    }
    
    /* Sleek buttons */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(135deg, #a67b5b, #c49a76) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(166, 123, 91, 0.4) !important;
        transition: all 0.3s ease !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(166, 123, 91, 0.6) !important;
        background: linear-gradient(135deg, #b98e6c, #d5ac88) !important;
    }
    
    /* Text input highlight */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 2px solid rgba(166, 123, 91, 0.3) !important;
        color: #5C4033 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    .stTextInput>div>div>input:focus {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: #a67b5b !important;
        box-shadow: 0 0 0 4px rgba(166, 123, 91, 0.15) !important;
    }
    
    /* Fix Table and Metric Text Colors */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] > div,
    table, th, td, .stTable, .stDataFrame {
        color: #4a332a !important;
        font-weight: 600 !important;
    }
    
    /* Labels, Text, and Placeholders */
    label, label p, .stMarkdown p, [data-testid="stWidgetLabel"] p, .stTextInput label p {
        color: #4a332a !important;
        font-weight: 600 !important;
    }
    ::placeholder {
        color: #8c7365 !important;
        opacity: 0.8 !important;
    }
    
    /* Hide some default elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Custom Main Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px; margin-top: 10px;">
    <div style="display: inline-block; padding: 25px 40px; background: rgba(255,255,255,0.3); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.4);">
        <h1 style="background: -webkit-linear-gradient(45deg, #8c5a2b, #d4a373); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 4rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 5px; line-height: 1.1;">🧪 StereoChem</h1>
        <p style="font-size: 1.3rem; color: #5C4033; margin-top: 5px; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px;">Molecular Stereochemistry Explorer</p>
        <hr style="border: none; border-top: 1px solid rgba(140, 90, 43, 0.2); margin: 12px 0;">
        <p style="font-size: 1.05rem; color: #8c5a2b; font-weight: 800; margin-top: 5px; margin-bottom: 0;">P.G.Dharshan &bull; RA2511026050012 &bull; AIML-A</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Note on public hosting
st.info("💡 **Pro Tip:** This app is fully cloud-native and rendering seamlessly on Streamlit Community Cloud.")

def load_artemisinin():
    st.session_state.smiles_input = "CC1CCC2C(C(OC(=O)C3C2(C)OOC13C)C)C"

# Input section
st.markdown("<h3 style='color: #613e25; margin-bottom: 5px;'>🔍 Analyze a Molecule</h3>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    smiles_input = st.text_input("Enter SMILES string:", key="smiles_input", placeholder="e.g. C1CCC(C1)C(C)O", label_visibility="collapsed")
with col2:
    st.button("✨ Load Artemisinin", on_click=load_artemisinin, use_container_width=True)

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
                        

                        
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
