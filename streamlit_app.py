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
        background: linear-gradient(135deg, #4A0E17, #1A0508) !important;
        background-attachment: fixed !important;
        color: #F8F0E3 !important;
    }
    
    /* Glassmorphism Main Container */
    .block-container {
        background: rgba(20, 0, 0, 0.4) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 800px !important;
    }
    
    /* Sleek buttons (Gold) */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(135deg, #D4AF37, #AA8022) !important;
        color: #330000 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
        transition: all 0.3s ease !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.5) !important;
        background: linear-gradient(135deg, #E5C158, #FFDF00) !important;
    }
    
    /* Text input highlight */
    .stTextInput>div>div>input {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 2px solid rgba(212, 175, 55, 0.4) !important;
        color: #F8F0E3 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    .stTextInput>div>div>input:focus {
        background: rgba(0, 0, 0, 0.5) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.2) !important;
    }
    
    /* Fix Table and Metric Text Colors */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] > div,
    table, th, td, .stTable, .stDataFrame {
        color: #F8F0E3 !important;
        font-weight: 600 !important;
    }
    
    /* Labels, Text, and Placeholders */
    label, label p, .stMarkdown p, [data-testid="stWidgetLabel"] p, .stTextInput label p, .stMarkdown h3 {
        color: #F8F0E3 !important;
        font-weight: 600 !important;
    }
    ::placeholder {
        color: #D4AF37 !important;
        opacity: 0.6 !important;
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
    <div style="display: inline-block; padding: 25px 40px; background: rgba(0,0,0,0.3); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid rgba(212,175,55,0.4);">
        <h1 style="background: -webkit-linear-gradient(45deg, #FFDF00, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 4rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 5px; line-height: 1.1;">🧪 StereoChem</h1>
        <p style="font-size: 1.3rem; color: #F8F0E3; margin-top: 5px; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px;">Molecular Stereochemistry Explorer</p>
        <hr style="border: none; border-top: 1px solid rgba(212, 175, 55, 0.3); margin: 12px 0;">
        <p style="font-size: 1.05rem; color: #D4AF37; font-weight: 800; margin-top: 5px; margin-bottom: 0;">P.G.Dharshan &bull; RA2511026050012 &bull; AIML-A</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Note on public hosting
st.info("💡 **Pro Tip:** This app is fully cloud-native and rendering seamlessly on Streamlit Community Cloud.")

def load_artemisinin():
    st.session_state.smiles_input = "C[C@@H]1CC[C@H]2[C@H](C(=O)O[C@H]3[C@@]24[C@H]1CC[C@](O3)(OO4)C)C"

# Input section
st.markdown("<h3 style='color: #D4AF37; margin-bottom: 5px;'>🔍 Analyze a Molecule</h3>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    smiles_input = st.text_input("Enter SMILES or Name:", key="smiles_input", placeholder="e.g. Aspirin or C1CCC(C1)C(C)O", label_visibility="collapsed")
with col2:
    st.button("✨ Load Artemisinin", on_click=load_artemisinin, use_container_width=True)

run_analysis = False
smiles_to_analyze = smiles_input

# Trigger analysis if user types and presses enter
if smiles_input and smiles_input.strip() != "":
    run_analysis = True

if run_analysis and smiles_to_analyze:
    with st.spinner('Fetching from PubChem & Analyzing molecule...'):
        try:
            import pubchempy as pcp
            import tempfile
            import os
            
            # Identify if input is SMILES or Name
            test_mol = Chem.MolFromSmiles(smiles_to_analyze)
            namespace = 'smiles' if test_mol is not None else 'name'
            
            with tempfile.NamedTemporaryFile(suffix='.sdf', delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                import requests
                # Download perfectly drawn 2D coordinates from PubChem
                pcp.download('SDF', tmp_path, smiles_to_analyze, namespace, record_type='2d', overwrite=True)
                suppl = Chem.SDMolSupplier(tmp_path)
                mol = next(suppl) if suppl else None
                
                # Fetch compound data for educational segment
                comp_req = pcp.get_compounds(smiles_to_analyze, namespace)
                compound_info = comp_req[0] if comp_req else None
                
                compound_description = ""
                if compound_info:
                    desc_res = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{compound_info.cid}/description/JSON")
                    if desc_res.status_code == 200:
                        desc_data = desc_res.json()
                        if 'InformationList' in desc_data and 'Information' in desc_data['InformationList']:
                            for info in desc_data['InformationList']['Information']:
                                if 'Description' in info:
                                    compound_description = info['Description']
                                    break
            except Exception as e:
                mol = None
                compound_info = None
                compound_description = ""
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            if mol is None:
                st.error("❌ Failed to load molecule from PubChem. Please check your query.")
            else:
                # Remove explicit hydrogens to make the 2D structure clear and uncluttered
                mol = Chem.RemoveHs(mol)
                
                # Assign stereochemistry from structure
                Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
                
                # Find chiral centers
                chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
                chiral_atoms = [center[0] for center in chiral_centers]
                
                # Mark chiral centers with their atom indices for clarity
                for atom_idx in chiral_atoms:
                    atom = mol.GetAtomWithIdx(atom_idx)
                    atom.SetProp('atomNote', str(atom_idx))
                
                # Generate Image
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
                        
                st.markdown("---")
                st.markdown("<h2 style='text-align: center; color: #D4AF37;'>📚 Educational Dashboard</h2>", unsafe_allow_html=True)
                
                # Create tabs for structured learning
                tab1, tab2, tab3, tab4 = st.tabs(["Compound Info", "Stereochemistry", "Chiral Centers", "R/S Configuration"])
                
                with tab1:
                    if compound_info:
                        if compound_description:
                            st.markdown("### Common Usage & Description")
                            st.info(compound_description)
                        st.markdown(f"**IUPAC Name:** {compound_info.iupac_name}")
                        st.markdown(f"**Molecular Formula:** {compound_info.molecular_formula}")
                        st.markdown(f"**Molecular Weight:** {compound_info.molecular_weight} g/mol")
                        if hasattr(compound_info, 'isomeric_smiles') and compound_info.isomeric_smiles:
                            st.markdown(f"**Isomeric SMILES:** `{compound_info.isomeric_smiles}`")
                    else:
                        st.info("Additional compound information could not be retrieved from PubChem.")
                
                with tab2:
                    st.markdown('''
                    **Stereochemistry** is a subdiscipline of chemistry that involves the study of the relative spatial arrangement of atoms that form the structure of molecules and their manipulation. 
                    It focuses on **stereoisomers**, which by definition have the same molecular formula and sequence of bonded atoms but differ in the three-dimensional orientations of their atoms in space.
                    ''')
                
                with tab3:
                    st.markdown('''
                    A **Chiral Center** (or stereocenter) is an atom that has four different groups bonded to it in such a manner that it has a non-superimposable mirror image.
                    In organic molecules, this is almost always a Carbon atom bonded to four uniquely different substituents. Identifying these centers is critical in fields like pharmacology, as different enantiomers of a drug can have vastly different biological effects.
                    ''')
                    
                with tab4:
                    st.markdown('''
                    The **R/S Configuration** system (Cahn-Ingold-Prelog priority rules) is the standard nomenclature used to unequivocally name enantiomers based on their 3D structure.
                    1. Assign priorities to the 4 groups attached to the chiral center based on atomic number (highest atomic number = highest priority).
                    2. Orient the molecule so that the lowest priority group (usually Hydrogen) is pointing away from you.
                    3. Determine the sequence of the remaining three priority groups from Highest (1) to Lowest (3).
                    - If the sequence is **Clockwise**, it is designated **(R)** (from Latin *rectus*, right).
                    - If the sequence is **Counter-Clockwise**, it's **(S)** (from Latin *sinister*, left).
                    ''')

                        
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
