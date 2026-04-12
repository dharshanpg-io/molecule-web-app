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

    
    /* Fix Table and Metric Text Colors */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] > div,
    table, th, td, .stTable, .stDataFrame {
        color: #5C4033 !important;
    }
    
    /* Labels, Text, and Placeholders */
    label, label p, .stMarkdown p, [data-testid="stWidgetLabel"] p, .stTextInput label p {
        color: #5C4033 !important;
    }
    ::placeholder {
        color: #5C4033 !important;
        opacity: 0.6 !important;
    }
    
    /* Hide some default elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Custom Main Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px; margin-top: 20px;">
    <h1 style="background: -webkit-linear-gradient(45deg, #8c5a2b, #d4a373); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 10px;">🧪 StereoChem</h1>
    <p style="font-size: 1.2rem; color: #5C4033; margin-top: -10px; font-weight: 500;">Molecular Stereochemistry Explorer</p>
    <p style="font-size: 1.1rem; color: #8c5a2b; font-weight: 700; margin-top: 10px;">P.G.Dharshan RA2511026050012 AIML-A</p>
</div>
""", unsafe_allow_html=True)

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
                        

                        
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
