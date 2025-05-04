document.addEventListener('DOMContentLoaded', function() {
    const crimesList = document.getElementById('crimes-list');
    const selectedCrimesList = document.getElementById('selected-crimes');
    const calcBtn = document.getElementById('calculate-btn');
    const resetBtn = document.getElementById('reset-btn');
    const timeValue = document.getElementById('time-value');
    const fineValue = document.getElementById('fine-value');
    const crimeCountValue = document.getElementById('crime-count-value');
    
    let crimeData = [];
    let selectedCrimes = [];
    
    // Verificar se os elementos existem
    const elementsExist = crimesList && selectedCrimesList && calcBtn && 
                         resetBtn && timeValue && fineValue && crimeCountValue;
    
    // Se estamos na página de administração, alguns elementos não existirão
    const isAdminPage = window.location.pathname.includes('/admin');
    
    // Add typing animation to hero section
    const heroTitle = document.querySelector('.hero-content h2');
    if (heroTitle) {
        const originalText = heroTitle.innerText;
        heroTitle.innerText = '';
        let i = 0;
        
        function typeWriter() {
            if (i < originalText.length) {
                heroTitle.innerHTML += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        
        setTimeout(typeWriter, 500);
    }
    
    // Fetch crimes data, apenas se estivermos na página principal 
    if (!isAdminPage && crimesList) {
        fetch('/crimes')
            .then(response => response.json())
            .then(data => {
                crimeData = data;
                renderCrimeCategories(data);
                
                // Update crime counts in stats
                const totalCrimes = document.getElementById('totalCrimes');
                const totalCategories = document.getElementById('totalCategories');
                
                if (totalCrimes) {
                    let count = 0;
                    data.forEach(category => {
                        count += category.crimes.length;
                    });
                    totalCrimes.innerText = count;
                }
                
                if (totalCategories) {
                    totalCategories.innerText = data.length;
                }
            })
            .catch(error => {
                console.error('Error fetching crimes data:', error);
                if (crimesList) {
                    crimesList.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> 
                            Error loading crimes data. Please refresh the page and try again.
                        </div>
                    `;
                }
            });
    }
    
    // Render crime categories
    function renderCrimeCategories(categories) {
        let html = '';
        
        categories.forEach(category => {
            html += `
                <div class="category-card">
                    <h3 class="category-title">
                        <i class="${category.icon}"></i> 
                        ${category.name}
                    </h3>
                    <div class="crimes-list">
            `;
            
            category.crimes.forEach(crime => {
                html += `
                    <div class="crime-item" id="crime-${crime.id}">
                        <label>
                            <input type="checkbox" class="crime-checkbox" 
                                data-id="${crime.id}" 
                                data-name="${crime.name}" 
                                data-time="${crime.time}" 
                                data-fine="${crime.fine}" 
                                data-category="${category.name}">
                            <div>
                                <div class="crime-name">${crime.name}</div>
                                <div class="crime-details">
                                    <span class="crime-time">
                                        <i class="fas fa-clock"></i> ${crime.time} meses
                                    </span>
                                    <span class="crime-fine">
                                        <i class="fas fa-dollar-sign"></i> R$${crime.fine.toLocaleString()}
                                    </span>
                                </div>
                                <div class="crime-description">${crime.description || ''}</div>
                            </div>
                        </label>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        crimesList.innerHTML = html;
        
        // Add event listeners to checkboxes
        document.querySelectorAll('.crime-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', handleCrimeSelection);
        });
    }
    
    // Handle crime selection
    function handleCrimeSelection(e) {
        const checkbox = e.target;
        const crimeId = checkbox.dataset.id;
        const crimeName = checkbox.dataset.name;
        const crimeTime = parseInt(checkbox.dataset.time);
        const crimeFine = parseInt(checkbox.dataset.fine);
        const crimeCategory = checkbox.dataset.category;
        
        const crimeElement = document.getElementById(`crime-${crimeId}`);
        
        if (checkbox.checked) {
            // Add to selected crimes
            crimeElement.classList.add('selected');
            
            const crimeData = {
                id: crimeId,
                name: crimeName,
                time: crimeTime,
                fine: crimeFine,
                category: crimeCategory
            };
            
            selectedCrimes.push(crimeData);
            updateSelectedCrimesList();
            
            // Animation
            crimeElement.classList.add('highlight-animation');
            setTimeout(() => {
                crimeElement.classList.remove('highlight-animation');
            }, 1500);
        } else {
            // Remove from selected crimes
            crimeElement.classList.remove('selected');
            selectedCrimes = selectedCrimes.filter(crime => crime.id !== crimeId);
            updateSelectedCrimesList();
        }
        
        // Update results
        calculateTotals();
    }
    
    // Update the selected crimes list
    function updateSelectedCrimesList() {
        if (selectedCrimes.length === 0) {
            selectedCrimesList.innerHTML = '<p>Nenhum crime selecionado</p>';
            return;
        }
        
        let html = '';
        selectedCrimes.forEach(crime => {
            html += `
                <div class="selected-crime-item">
                    <div class="selected-crime-name">${crime.name}</div>
                    <div class="selected-crime-time">${crime.time} meses</div>
                    <div class="selected-crime-fine">R$${crime.fine.toLocaleString()}</div>
                    <div class="remove-crime" data-id="${crime.id}">
                        <i class="fas fa-times"></i>
                    </div>
                </div>
            `;
        });
        
        selectedCrimesList.innerHTML = html;
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-crime').forEach(button => {
            button.addEventListener('click', function() {
                const crimeId = this.dataset.id;
                const checkbox = document.querySelector(`.crime-checkbox[data-id="${crimeId}"]`);
                
                if (checkbox) {
                    checkbox.checked = false;
                    const event = new Event('change');
                    checkbox.dispatchEvent(event);
                }
            });
        });
    }
    
    // Calculate total time and fine
    function calculateTotals() {
        let totalTime = 0;
        let totalFine = 0;
        
        selectedCrimes.forEach(crime => {
            totalTime += crime.time;
            totalFine += crime.fine;
        });
        
        timeValue.textContent = `${totalTime} meses`;
        fineValue.textContent = `R$${totalFine.toLocaleString()}`;
        crimeCountValue.textContent = selectedCrimes.length;
    }
    
    // Calculate button
    if (elementsExist && !isAdminPage) {
        calcBtn.addEventListener('click', function() {
            calculateTotals();
            
            // Scroll to results section
            document.getElementById('results-section').scrollIntoView({
                behavior: 'smooth'
            });
            
            // Flash animation
            const resultsSection = document.getElementById('results-section');
            resultsSection.style.backgroundColor = '#2c3e50';
            setTimeout(() => {
                resultsSection.style.backgroundColor = '#2d2d2d';
            }, 300);
        });
        
        // Reset button
        resetBtn.addEventListener('click', function() {
        Swal.fire({
            title: 'Limpar seleção?',
            text: 'Todos os crimes selecionados serão removidos.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#3b82f6',
            confirmButtonText: 'Sim, limpar',
            cancelButtonText: 'Cancelar',
            background: '#1e293b',
            color: '#f1f5f9'
        }).then((result) => {
            if (result.isConfirmed) {
                // Uncheck all checkboxes
                document.querySelectorAll('.crime-checkbox').forEach(checkbox => {
                    checkbox.checked = false;
                    const crimeElement = document.getElementById(`crime-${checkbox.dataset.id}`);
                    if (crimeElement) {
                        crimeElement.classList.remove('selected');
                    }
                });
                
                // Clear selected crimes
                selectedCrimes = [];
                updateSelectedCrimesList();
                
                // Reset totals
                timeValue.textContent = '0 meses';
                fineValue.textContent = 'R$0';
                crimeCountValue.textContent = '0';
                
                // Reset chart if exists
                if (window.penaltyChart) {
                    window.penaltyChart.data.datasets[0].data = [0, 0];
                    window.penaltyChart.update();
                }
                
                // Show success message
                Swal.fire({
                    position: 'top-end',
                    icon: 'success',
                    title: 'Seleção limpa com sucesso',
                    showConfirmButton: false,
                    timer: 1500,
                    background: '#1e293b',
                    color: '#f1f5f9'
                });
            }
        });
    });
    }
});
