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
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    
    /* Sleek buttons */
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.6) !important;
    }
    
    /* Text input glow */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00c6ff !important;
        box-shadow: 0 0 10px rgba(0, 198, 255, 0.5) !important;
    }
    
    /* ID Card in Sidebar */
    .id-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 20px;
        margin-top: 20px;
        text-align: center;
        color: white;
    }
    .id-card h3 { margin-bottom: 5px; color: #00c6ff; font-weight: 700;}
    .id-card p { margin: 8px 0; font-size: 0.95rem; color: #e0e0e0; }
    .id-name { font-weight: 800; font-size: 1.3rem !important; color: #fff !important; letter-spacing: 1px;}
    
    /* Hide some default elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Custom Main Header
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; margin-top: 20px;">
    <h1 style="background: -webkit-linear-gradient(45deg, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 10px;">🧪 StereoChem</h1>
    <p style="font-size: 1.2rem; color: #a0aec0; margin-top: -10px; font-weight: 500;">Molecular Stereochemistry Explorer</p>
</div>
""", unsafe_allow_html=True)

# Student Details Sidebar
with st.sidebar:
    st.markdown("""
    <div class="id-card">
        <h3>👨‍🎓 Student Profile</h3>
        <p class="id-name">P.G. Dharshan</p>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
        <p><b>Reg No:</b> RA2511026050012</p>
        <p><b>Class/Sec:</b> AIML-A</p>
        <p><b>Year/Sem:</b> I / II</p>
    </div>
    """, unsafe_allow_html=True)

# Note on public hosting
st.info("💡 **Pro Tip:** This app is fully cloud-native and rendering seamlessly on Streamlit Community Cloud.")

# Input section
smiles_input = st.text_input("Enter SMILES string:", value="", placeholder="e.g. C1CCC(C1)C(C)O")

# Try-out buttons
st.markdown("**Or try these examples:**")
col1, col2 = st.columns(2)
run_analysis = False
smiles_to_analyze = smiles_input

with col1:
    if st.button("Artemisinin"):
        smiles_to_analyze = "CC1CCC2C(C1)C3CCC4=CC(=O)OC5C4C3(C2O5)O"
        run_analysis = True
with col2:
    if st.button("Antibiotic fragment"):
        smiles_to_analyze = "CC(C)CC1C(=O)NC(C(=O)NC(C(=O)O)C(C)O)C(C)C"
        run_analysis = True

# Also trigger analysis if user types and presses enter
if smiles_input and smiles_input != "":
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
