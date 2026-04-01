import streamlit as st
import io
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem

# Configure the Streamlit page
st.set_page_config(page_title="StereoChem Explorer", page_icon="🧪", layout="centered")

st.title("🧪 StereoChem Explorer")
st.markdown("Analyze molecular stereochemistry interactively.")

# Note on public hosting
st.info("💡 **Ready for the public?** You can instantly host this app for free on [Streamlit Community Cloud](https://share.streamlit.io/) to get a permanent public link!")

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
