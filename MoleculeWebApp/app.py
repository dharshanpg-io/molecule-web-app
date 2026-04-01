import io
import base64
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem

app = Flask(__name__)
CORS(app)

class MoleculeAnalyzer:
    def __init__(self, smiles):
        self.smiles = smiles
        self.molecule = None
        self.chiral_centers = []
        self.error_msg = None

    def load_molecule(self):
        try:
            mol = Chem.MolFromSmiles(self.smiles)
            if mol is None:
                self.error_msg = f"Failed to load molecule from SMILES: {self.smiles}"
                return False
            
            self.molecule = Chem.AddHs(mol)
            AllChem.EmbedMolecule(self.molecule, randomSeed=42)
            Chem.AssignStereochemistryFrom3D(self.molecule)
            AllChem.Compute2DCoords(self.molecule)
            return True
        except Exception as e:
            self.error_msg = f"Error loading molecule: {str(e)}"
            return False

    def find_chiral_centers(self):
        if self.molecule is None:
            return
        self.chiral_centers = Chem.FindMolChiralCenters(self.molecule, includeUnassigned=True)

    def draw_molecule_base64(self):
        if self.molecule is None:
            return None

        chiral_atoms = [center[0] for center in self.chiral_centers]
        try:
            img = Draw.MolToImage(
                self.molecule, 
                highlightAtoms=chiral_atoms,
                size=(600, 600)
            )
            
            # Save to BytesIO
            img_io = io.BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)
            
            # Encode to Base64
            img_b64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
            
        except Exception as e:
            self.error_msg = f"Error generating image: {str(e)}"
            return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_molecule():
    data = request.get_json()
    if not data or 'smiles' not in data:
        return jsonify({"success": False, "error": "Missing 'smiles' in request body"}), 400

    smiles = data['smiles'].strip()
    if not smiles:
        return jsonify({"success": False, "error": "SMILES string cannot be empty"}), 400

    analyzer = MoleculeAnalyzer(smiles)
    if not analyzer.load_molecule():
        return jsonify({"success": False, "error": analyzer.error_msg}), 400

    analyzer.find_chiral_centers()
    
    # Format chiral centers for frontend
    centers_data = []
    for center in analyzer.chiral_centers:
        atom_idx, config = center
        if config == '?':
            config = 'Unassigned'
        centers_data.append({
            "atom_idx": atom_idx,
            "configuration": config
        })

    img_b64 = analyzer.draw_molecule_base64()
    if not img_b64 and analyzer.error_msg:
         return jsonify({"success": False, "error": analyzer.error_msg}), 500

    return jsonify({
        "success": True,
        "smiles": smiles,
        "num_chiral_centers": len(centers_data),
        "chiral_centers": centers_data,
        "image_base64": img_b64
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
