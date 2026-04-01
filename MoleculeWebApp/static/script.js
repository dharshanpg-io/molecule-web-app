document.addEventListener('DOMContentLoaded', () => {
    const smilesInput = document.getElementById('smiles-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');
    const errorMsg = document.getElementById('error-msg');
    const resultsSection = document.getElementById('results-section');
    const molImage = document.getElementById('mol-image');
    const chiralCount = document.getElementById('chiral-count');
    const configTbody = document.getElementById('config-tbody');
    const tryBtns = document.querySelectorAll('.try-btn');

    // Handle suggestion buttons
    tryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            smilesInput.value = btn.getAttribute('data-smiles');
            performAnalysis();
        });
    });

    // Handle Enter key
    smilesInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performAnalysis();
        }
    });

    // Handle analyze click
    analyzeBtn.addEventListener('click', performAnalysis);

    async function performAnalysis() {
        const smiles = smilesInput.value.trim();
        
        if (!smiles) {
            showError("Please enter a SMILES string.");
            smilesInput.focus();
            return;
        }

        // Setup UI for loading
        setLoadingState(true);
        hideError();
        
        try {
            // Note: Since frontend and backend run on same host, we use relative URL path or local API
            // Usually, Flask serves on :5000 and we might access via /api/analyze if we serve via Flask
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ smiles })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "An unknown error occurred.");
            }

            // Populate Results
            populateResults(data);

        } catch (error) {
            console.error("Analysis error:", error);
            showError(error.message);
            resultsSection.classList.add('hidden');
        } finally {
            setLoadingState(false);
        }
    }

    function populateResults(data) {
        // Image
        molImage.src = data.image_base64;
        
        // Count
        chiralCount.textContent = data.num_chiral_centers;
        
        // Table
        configTbody.innerHTML = '';
        
        if (data.num_chiral_centers === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="2" style="text-align: center; color: var(--text-secondary);">No chiral centers found.</td>`;
            configTbody.appendChild(tr);
        } else {
            data.chiral_centers.forEach(center => {
                const tr = document.createElement('tr');
                
                let configClass = '';
                if (center.configuration === 'R') configClass = 'config-r';
                else if (center.configuration === 'S') configClass = 'config-s';
                else configClass = 'config-unassigned';

                tr.innerHTML = `
                    <td>Atom ${center.atom_idx}</td>
                    <td class="${configClass}">${center.configuration}</td>
                `;
                configTbody.appendChild(tr);
            });
        }

        // Show Results section with animation
        resultsSection.classList.remove('hidden');
        
        // Reset animation logic
        const elements = document.querySelectorAll('.fade-in-up');
        elements.forEach(el => {
            el.style.animation = 'none';
            el.offsetHeight; /* trigger reflow */
            el.style.animation = null; 
        });
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
            analyzeBtn.disabled = true;
            smilesInput.disabled = true;
        } else {
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
            analyzeBtn.disabled = false;
            smilesInput.disabled = false;
        }
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    function hideError() {
        errorMsg.textContent = '';
        errorMsg.classList.add('hidden');
    }
});
