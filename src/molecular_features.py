"""
Molecular Feature Extraction Module
Provides RDKit-based calculation of physicochemical descriptors,
Morgan fingerprints, Lipinski compliance, and 2D molecular structure rendering.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import base64

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, AllChem, Draw
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


def validate_smiles(smiles: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a SMILES string and return canonical SMILES if valid.
    
    Args:
        smiles: Chemical SMILES string
        
    Returns:
        Tuple of (is_valid: bool, canonical_smiles: Optional[str])
    """
    if not RDKIT_AVAILABLE or not isinstance(smiles, str) or not smiles.strip():
        return False, None
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            return False, None
        canonical = Chem.MolToSmiles(mol, canonical=True)
        return True, canonical
    except Exception:
        return False, None


def calculate_descriptors(smiles: str) -> Optional[Dict[str, Any]]:
    """
    Calculate physicochemical descriptors for a valid SMILES string.
    
    Descriptors:
        - MW: Molecular Weight (g/mol)
        - LogP: Octanol-water partition coefficient
        - HBD: Number of Hydrogen Bond Donors
        - HBA: Number of Hydrogen Bond Acceptors
        - RotB: Number of Rotatable Bonds
        - TPSA: Topological Polar Surface Area (Å²)
        - LipinskiPassRate: Fraction of Lipinski's Rule of 5 criteria met (0.0 to 1.0)
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary of descriptors or None if SMILES is invalid
    """
    if not RDKIT_AVAILABLE or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            return None
            
        mw = float(Descriptors.MolWt(mol))
        logp = float(Descriptors.MolLogP(mol))
        hbd = int(Lipinski.NumHDonors(mol))
        hba = int(Lipinski.NumHAcceptors(mol))
        rotb = int(Lipinski.NumRotatableBonds(mol))
        tpsa = float(Descriptors.TPSA(mol))
        
        # Lipinski Rule of 5 evaluations
        # 1. MW <= 500
        # 2. LogP <= 5.0
        # 3. HBD <= 5
        # 4. HBA <= 10
        # Rotatable bonds <= 10 (Veber rule extension)
        violations = 0
        if mw > 500:
            violations += 1
        if logp > 5.0:
            violations += 1
        if hbd > 5:
            violations += 1
        if hba > 10:
            violations += 1
        if rotb > 10:
            violations += 1
            
        lipinski_score = (5 - violations) / 5.0
        
        return {
            "MW": round(mw, 3),
            "LogP": round(logp, 3),
            "HBD": hbd,
            "HBA": hba,
            "RotB": rotb,
            "TPSA": round(tpsa, 3),
            "LipinskiViolations": violations,
            "LipinskiPassRate": round(lipinski_score, 2),
            "CanonicalSMILES": Chem.MolToSmiles(mol, canonical=True)
        }
    except Exception:
        return None


def generate_morgan_fingerprint(smiles: str, radius: int = 2, n_bits: int = 512) -> Optional[np.ndarray]:
    """
    Generate Morgan fingerprint as a binary numpy array.
    
    Args:
        smiles: SMILES string
        radius: Morgan radius (default 2, corresponding to ECFP4)
        n_bits: Length of bit vector (default 512)
        
    Returns:
        numpy 1D array of length n_bits with 0/1 entries, or None if invalid
    """
    if not RDKIT_AVAILABLE or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            return None
        try:
            from rdkit.Chem import rdFingerprintGenerator
            gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
            fp = gen.GetFingerprint(mol)
        except Exception:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
            
        arr = np.zeros((n_bits,), dtype=np.int8)
        for bit in fp.GetOnBits():
            arr[bit] = 1
        return arr
    except Exception:
        return None


def get_molecule_svg(smiles: str, width: int = 300, height: int = 250) -> Optional[str]:
    """
    Generate an SVG image representation of a molecule for web UI rendering.
    
    Args:
        smiles: SMILES string
        width: Image width in px
        height: Image height in px
        
    Returns:
        SVG string XML or None if invalid
    """
    if not RDKIT_AVAILABLE or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            return None
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addAtomIndices = False
        drawer.drawOptions().bondLineWidth = 2
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg
    except Exception:
        return None
