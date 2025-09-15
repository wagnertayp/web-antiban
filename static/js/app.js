// WhatsApp Sender Application
class WhatsAppSender {
    constructor() {
        this.leads = [];
        this.validationErrors = [];
        this.connectionData = null;
        this.tabNumber = this.getTabNumber();
        this.maxLeadsPerTab = 1000;
        
        this.initializeEventListeners();
        this.checkSavedConnection();
        this.setupTabOptimization();
    }
    
    getTabNumber() {
        // Generate tab number based on URL parameters or random
        const urlParams = new URLSearchParams(window.location.search);
        const tabParam = urlParams.get('tab');
        if (tabParam) {
            return parseInt(tabParam);
        }
        // Generate random tab number for identification
        return Math.floor(Math.random() * 20) + 1;
    }
    
    setupTabOptimization() {
        // Show tab indicator
        const tabIndicator = document.getElementById('tabIndicator');
        const tabStrategy = document.getElementById('tabStrategy');
        
        if (tabIndicator) {
            tabIndicator.textContent = `Sistema Otimizado`;
            tabIndicator.style.display = 'inline-block';
        }
        
        if (tabStrategy) {
            tabStrategy.style.display = 'inline-block';
        }
        
        // Show smart distribution panel
        const smartDistributionPanel = document.getElementById('smartDistributionPanel');
        if (smartDistributionPanel) {
            smartDistributionPanel.style.display = 'block';
        }
        
        // Remove old tab number references
        // phoneSelectionTabNumber removed from interface
        
        // Add lead count warning
        this.addLeadCountMonitoring();
    }
    
    addLeadCountMonitoring() {
        const leadsInput = document.getElementById('leadsInput');
        if (leadsInput) {
            leadsInput.addEventListener('input', () => {
                this.checkLeadCount();
            });
        }
    }
    
    checkLeadCount() {
        const leadsText = document.getElementById('leadsInput').value;
        const lines = leadsText.split('\n').filter(line => line.trim());
        const leadCount = lines.length;
        
        // Show warning if exceeding recommended limit
        let warningElement = document.getElementById('leadCountWarning');
        if (!warningElement) {
            warningElement = document.createElement('div');
            warningElement.id = 'leadCountWarning';
            warningElement.className = 'alert alert-warning mt-2';
            document.getElementById('leadsInput').parentNode.appendChild(warningElement);
        }
        
        if (leadCount > this.maxLeadsPerTab) {
            warningElement.innerHTML = `
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Atenção:</strong> ${leadCount} contatos detectados. 
                Para otimização, recomendamos até ${this.maxLeadsPerTab} contatos por aba.
                <br><small>Considere dividir em mais abas para velocidade máxima.</small>
            `;
            warningElement.style.display = 'block';
        } else if (leadCount > 0) {
            warningElement.innerHTML = `
                <i class="fas fa-info-circle me-2"></i>
                <strong>Aba #${this.tabNumber}:</strong> ${leadCount} contatos carregados. 
                Otimizado para processamento em paralelo.
            `;
            warningElement.className = 'alert alert-info mt-2';
            warningElement.style.display = 'block';
        } else {
            warningElement.style.display = 'none';
        }
    }
    
    generateTabUrls() {
        if (!this.connectionData || !this.connectionData.phone_numbers) {
            this.showAlert('Conecte-se primeiro para gerar URLs das abas', 'warning');
            return;
        }
        
        const phoneNumbers = this.connectionData.phone_numbers;
        const baseUrl = window.location.origin + window.location.pathname;
        
        let urlsHtml = `
            <div class="modal fade" id="tabUrlsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-external-link-alt me-2"></i>
                                URLs para 20 Abas (Estratégia Máxima Velocidade)
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                <i class="fas fa-lightbulb me-2"></i>
                                <strong>Instrução:</strong> Abra cada URL em uma nova aba do navegador. 
                                Cada aba será otimizada para usar 1 número específico com até 1000 contatos.
                            </div>
                            <div class="row">
        `;
        
        phoneNumbers.forEach((phone, index) => {
            const tabNumber = index + 1;
            const url = `${baseUrl}?tab=${tabNumber}&phone=${phone.id}`;
            urlsHtml += `
                <div class="col-md-6 mb-2">
                    <div class="card border-primary">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">Aba ${tabNumber}</h6>
                            <small class="text-muted">Phone: ${phone.display_phone_number}</small>
                            <div class="input-group input-group-sm mt-1">
                                <input type="text" class="form-control" value="${url}" readonly>
                                <button class="btn btn-outline-primary" onclick="navigator.clipboard.writeText('${url}')">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button class="btn btn-primary" onclick="window.open('${url}', '_blank')">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        urlsHtml += `
                            </div>
                            <div class="mt-3">
                                <button type="button" class="btn btn-success" onclick="this.openAllTabs()">
                                    <i class="fas fa-rocket me-2"></i>
                                    Abrir Todas as 20 Abas de Uma Vez
                                </button>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if it exists
        const existingModal = document.getElementById('tabUrlsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', urlsHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('tabUrlsModal'));
        modal.show();
    }
    
    openAllTabs() {
        if (!this.connectionData || !this.connectionData.phone_numbers) return;
        
        const phoneNumbers = this.connectionData.phone_numbers;
        const baseUrl = window.location.origin + window.location.pathname;
        
        phoneNumbers.forEach((phone, index) => {
            const tabNumber = index + 1;
            const url = `${baseUrl}?tab=${tabNumber}&phone=${phone.id}`;
            setTimeout(() => {
                window.open(url, '_blank');
            }, index * 300); // 300ms delay between tabs
        });
        
        this.showAlert(`Abrindo ${phoneNumbers.length} abas para velocidade máxima!`, 'success');
    }
    
    showTabOptimizationTips() {
        const tipsHtml = `
            <div class="modal fade" id="optimizationTipsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-rocket me-2"></i>
                                Dicas de Otimização - Estratégia 20 Abas
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-success">
                                <h6><i class="fas fa-trophy me-2"></i>Velocidade Máxima: 20.000 mensagens simultâneas</h6>
                            </div>
                            
                            <h6><i class="fas fa-phone me-2"></i>Configuração de Números:</h6>
                            <ul class="small">
                                <li>Use <strong>1 número por aba</strong> para evitar conflitos</li>
                                <li>Cada aba processará independentemente</li>
                                <li>Máximo 1000 contatos por número</li>
                            </ul>
                            
                            <h6><i class="fas fa-list me-2"></i>Divisão de Contatos:</h6>
                            <ul class="small">
                                <li>Divida sua lista em grupos de até 1000</li>
                                <li>Cole cada grupo em uma aba diferente</li>
                                <li>Use templates diferentes para variação</li>
                            </ul>
                            
                            <h6><i class="fas fa-clock me-2"></i>Timing:</h6>
                            <ul class="small">
                                <li>Inicie todas as abas simultaneamente</li>
                                <li>Velocidade: ~333 mensagens/segundo por aba</li>
                                <li>Total: ~6.660 mensagens/segundo (todas abas)</li>
                            </ul>
                            
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <strong>Importante:</strong> Use templates aprovados e respeite limites do WhatsApp.
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Entendi</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if it exists
        const existingModal = document.getElementById('optimizationTipsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', tipsHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('optimizationTipsModal'));
        modal.show();
    }
    
    initializeEventListeners() {
        // Connection buttons
        const connectBtn = document.getElementById('connectButton');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => {
                this.connectWhatsApp();
            });
        }
        
        const disconnectBtn = document.getElementById('disconnectButton');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => {
                this.disconnect();
            });
        }
        
        // Validate leads button
        const validateBtn = document.getElementById('validateLeadsBtn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => {
                this.validateLeads();
            });
        }
        
        // Smart Distribution button
        const smartBtn = document.getElementById('smartDistributionBtn');
        if (smartBtn) {
            smartBtn.addEventListener('click', () => {
                this.sendSmartDistribution();
            });
        }
        
        // Template selection buttons
        const selectAllBtn = document.getElementById('selectAllTemplatesBtn');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                this.selectAllTemplates();
            });
        }
        
        const clearBtn = document.getElementById('clearTemplatesBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearTemplateSelection();
            });
        }
        
        // Leads textarea change
        const leadsInput = document.getElementById('leadsInput');
        if (leadsInput) {
            leadsInput.addEventListener('input', () => {
                this.resetValidation();
                this.checkLeadCount();
            });
        }
        
        // Add tab optimization buttons
        const optimizationBtn = document.getElementById('tabOptimizationBtn');
        if (optimizationBtn) {
            optimizationBtn.addEventListener('click', () => {
                this.showTabOptimizationTips();
            });
        }
        
        // Generate tab URLs button
        const generateTabUrlsBtn = document.getElementById('generateTabUrlsBtn');
        if (generateTabUrlsBtn) {
            generateTabUrlsBtn.addEventListener('click', () => {
                this.generateTabUrls();
            });
        }
        
        // Test proxy button
        const testProxyBtn = document.getElementById('testProxyBtn');
        if (testProxyBtn) {
            testProxyBtn.addEventListener('click', () => {
                this.testProxy();
            });
        }
    }

    async connectWhatsApp() {
        const accessToken = document.getElementById('accessToken').value.trim();
        const businessManagerId = document.getElementById('businessManagerId').value.trim();
        const proxyConnection = document.getElementById('proxyConnection').value.trim();
        
        if (!accessToken) {
            this.showAlert('Token de acesso é obrigatório', 'danger');
            return;
        }
        
        const connectButton = document.getElementById('connectButton');
        const originalText = connectButton.innerHTML;
        connectButton.disabled = true;
        connectButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Conectando...';
        
        try {
            const response = await fetch('/api/connect-whatsapp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    access_token: accessToken,
                    business_manager_id: businessManagerId || null,
                    proxy_connection: proxyConnection || null
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.connectionData = result.data;
                localStorage.setItem('whatsapp_connection', JSON.stringify(this.connectionData));
                this.updateConnectionUI(true);
                this.loadConnectionData();
                this.showAlert('Conectado com sucesso! Carregando dados...', 'success');
            } else {
                // Check for token expiration
                if (response.status === 401 || result.message.includes('expired') || result.message.includes('access token')) {
                    this.showAlert('⚠️ TOKEN EXPIRADO: Seu token WhatsApp expirou. Por favor, obtenha um novo token do Facebook Business Manager.', 'warning');
                } else {
                    this.showAlert(result.message || 'Erro ao conectar', 'danger');
                }
            }
        } catch (error) {
            console.error('Erro de conexão:', error);
            this.showAlert('Erro de conexão com o servidor', 'danger');
        } finally {
            connectButton.disabled = false;
            connectButton.innerHTML = originalText;
        }
    }
    
    disconnect() {
        this.connectionData = null;
        localStorage.removeItem('whatsapp_connection');
        this.updateConnectionUI(false);
        this.clearConnectionData();
        this.showAlert('Desconectado com sucesso', 'info');
    }
    
    checkSavedConnection() {
        const savedConnection = localStorage.getItem('whatsapp_connection');
        if (savedConnection) {
            try {
                this.connectionData = JSON.parse(savedConnection);
                this.updateConnectionUI(true);
                this.loadConnectionData();
            } catch (error) {
                console.error('Erro ao carregar conexão salva:', error);
                localStorage.removeItem('whatsapp_connection');
            }
        }
    }
    
    updateConnectionUI(connected) {
        const connectionStatus = document.getElementById('connectionStatus');
        const connectionInfo = document.getElementById('connectionInfo');
        const accessToken = document.getElementById('accessToken');
        const businessManagerId = document.getElementById('businessManagerId');
        const connectButton = document.getElementById('connectButton');
        
        if (connected && this.connectionData) {
            connectionStatus.className = 'badge bg-success';
            connectionStatus.textContent = 'Conectado';
            connectionInfo.style.display = 'block';
            
            // Ocultar campos de entrada
            accessToken.parentElement.style.display = 'none';
            businessManagerId.parentElement.style.display = 'none';
            connectButton.parentElement.style.display = 'none';
            
            // Preencher informações de conexão
            document.getElementById('connectedBmId').textContent = this.connectionData.business_manager_id;
            document.getElementById('connectedPhones').textContent = this.connectionData.phone_numbers.length;
            document.getElementById('connectedTemplates').textContent = this.connectionData.templates.length;
            
            // Popular números e templates
            this.populatePhoneNumbers(this.connectionData.phone_numbers);
            this.populateTemplates(this.connectionData.templates);
        } else {
            connectionStatus.className = 'badge bg-secondary';
            connectionStatus.textContent = 'Desconectado';
            connectionInfo.style.display = 'none';
            
            // Mostrar campos de entrada
            accessToken.parentElement.style.display = 'block';
            businessManagerId.parentElement.style.display = 'block';
            connectButton.parentElement.style.display = 'block';
            
            // Limpar campos
            accessToken.value = '';
            businessManagerId.value = '';
            
            // Limpar números e templates
            this.clearConnectionData();
        }
    }
    
    populatePhoneNumbers(phoneNumbers) {
        const container = document.getElementById('phoneNumbersContainer');
        const countBadge = document.getElementById('phoneNumbersCount');
        
        if (!phoneNumbers || phoneNumbers.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-2">Nenhum número encontrado</div>';
            if (countBadge) countBadge.textContent = '0';
            return;
        }
        
        // Update count
        if (countBadge) countBadge.textContent = phoneNumbers.length;
        
        let html = '';
        phoneNumbers.forEach((phone, index) => {
            const qualityBadge = phone.quality_rating === 'GREEN' ? 'bg-success' : 
                               phone.quality_rating === 'YELLOW' ? 'bg-warning' : 'bg-secondary';
            
            html += `
                <div class="d-flex align-items-center justify-content-between mb-2 p-2 bg-dark rounded">
                    <div>
                        <strong>${phone.display_phone_number}</strong>
                        ${phone.verified_name ? `<br><small class="text-muted">${phone.verified_name}</small>` : ''}
                        <br><small class="text-info">ID: ${phone.id.slice(0, 15)}...</small>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge ${qualityBadge}">${phone.quality_rating || 'UNKNOWN'}</span>
                        <span class="badge bg-primary">ATIVO</span>
                    </div>
                </div>
            `;
        });
        
        // Add smart distribution info
        html += `
            <div class="alert alert-success mt-3 small">
                <i class="fas fa-magic me-2"></i>
                <strong>Distribuição Automática:</strong> Sistema usará TODOS os ${phoneNumbers.length} números automaticamente. 
                Máximo de 1000 mensagens por número = Capacidade total: ${phoneNumbers.length * 1000} mensagens.
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    populateTemplates(templates) {
        const container = document.getElementById('templatesContainer');
        
        if (!templates || templates.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-2">Nenhum template aprovado encontrado</div>';
            document.getElementById('selectAllTemplatesBtn').disabled = true;
            document.getElementById('clearTemplatesBtn').disabled = true;
            return;
        }
        
        let html = '';
        templates.forEach(template => {
            const categoryBadge = template.category === 'MARKETING' ? 'bg-primary' : 
                                template.category === 'UTILITY' ? 'bg-success' : 'bg-info';
            
            html += `
                <div class="form-check d-flex align-items-center justify-content-between mb-2">
                    <div>
                        <input class="form-check-input template-checkbox" type="checkbox" value="${template.name}" id="template_${template.name}">
                        <label class="form-check-label ms-2" for="template_${template.name}">
                            <strong>${template.name}</strong>
                            <small class="text-muted d-block">${template.language} | ${template.category}</small>
                        </label>
                    </div>
                    <div>
                        <span class="badge ${categoryBadge} me-1">${template.category}</span>
                        ${template.has_buttons ? '<i class="fas fa-link text-primary" title="Tem botões"></i>' : ''}
                        ${template.has_parameters ? '<i class="fas fa-code text-info" title="Tem parâmetros"></i>' : ''}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        document.getElementById('selectAllTemplatesBtn').disabled = false;
        document.getElementById('clearTemplatesBtn').disabled = false;
        this.addTemplateEventListeners();
    }
    
    addPhoneNumberEventListeners() {
        const radios = document.querySelectorAll('.phone-radio');
        radios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateDistributionInfo();
                // Update tab indicator when phone selection changes
                this.updateTabIndicator();
            });
        });
    }
    
    updateTabIndicator() {
        const selectedPhone = document.querySelector('.phone-radio:checked');
        if (selectedPhone && this.connectionData) {
            const phoneData = this.connectionData.phone_numbers.find(p => p.id === selectedPhone.value);
            if (phoneData) {
                const tabIndicator = document.getElementById('tabIndicator');
                if (tabIndicator) {
                    tabIndicator.innerHTML = `Aba #${this.tabNumber} - ${phoneData.display_phone_number}`;
                }
            }
        }
    }
    
    addTemplateEventListeners() {
        const checkboxes = document.querySelectorAll('.template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
                this.updateTemplateButtons();
            });
        });
    }
    
    clearConnectionData() {
        const phoneContainer = document.getElementById('phoneNumbersContainer');
        if (phoneContainer) {
            phoneContainer.innerHTML = '<div class="text-muted text-center py-2"><i class="fas fa-plug me-1"></i>Conecte-se primeiro para ver os números disponíveis</div>';
        }
        
        const templateContainer = document.getElementById('templatesContainer');
        if (templateContainer) {
            templateContainer.innerHTML = '<div class="text-muted text-center py-2"><i class="fas fa-plug me-1"></i>Conecte-se primeiro para ver os templates disponíveis</div>';
        }
        
        document.getElementById('selectAllTemplatesBtn').disabled = true;
        document.getElementById('clearTemplatesBtn').disabled = true;
    }
    
    loadConnectionData() {
        if (this.connectionData) {
            console.log(`${this.connectionData.phone_numbers.length} phone numbers carregados da conexão`);
            this.updateDistributionInfo();
        }
    }
    
    async validateLeads() {
        console.log('🔍 validateLeads called');
        
        const leadsText = document.getElementById('leadsInput').value.trim();
        console.log('📝 Leads text:', leadsText.substring(0, 100));
        
        if (!leadsText) {
            console.log('❌ No leads text provided');
            this.showAlert('Por favor, insira a lista de leads', 'warning');
            return;
        }
        
        const btn = document.getElementById('validateLeadsBtn');
        if (!btn) {
            console.error('❌ Validate button not found!');
            return;
        }
        
        const originalText = btn.innerHTML;
        console.log('🔄 Starting validation...');
        
        btn.classList.add('btn-loading');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Validando...';
        
        try {
            console.log('📡 Sending request to /api/validate-leads');
            const response = await fetch('/api/validate-leads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ leads: leadsText })
            });
            
            console.log('📊 Response status:', response.status);
            const result = await response.json();
            console.log('📋 Result:', result);
            
            if (response.ok) {
                this.leads = result.leads;
                this.validationErrors = result.errors;
                console.log('✅ Validation successful, displaying results');
                this.displayValidationResults(result);
            } else {
                console.log('❌ Validation failed:', result.error);
                this.showAlert(result.error || 'Erro na validação', 'danger');
            }
            
        } catch (error) {
            console.error('❌ Error validating leads:', error);
            this.showAlert('Erro de conexão com o servidor', 'danger');
        } finally {
            console.log('🏁 Validation finished');
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
    
    displayValidationResults(result) {
        console.log('📊 displayValidationResults called with:', result);
        
        const validationDiv = document.getElementById('leadsValidation');
        if (!validationDiv) {
            console.error('❌ leadsValidation div not found!');
            return;
        }
        
        console.log('🔢 Updating counters...');
        
        // Update counters with null checks
        const validCountEl = document.getElementById('validCount');
        const errorCountEl = document.getElementById('errorCount');
        const totalCountEl = document.getElementById('totalCount');
        
        if (validCountEl) validCountEl.textContent = result.total_valid;
        if (errorCountEl) errorCountEl.textContent = result.total_errors;
        if (totalCountEl) totalCountEl.textContent = result.original_count || (result.total_valid + result.total_errors);
        
        // Show validation div
        console.log('👁️ Showing validation div...');
        validationDiv.classList.remove('d-none');
        
        // Update distribution info
        console.log('📈 Updating distribution info...');
        this.updateDistributionInfo();
        
        // Show errors if any
        if (result.errors && result.errors.length > 0) {
            console.log(`⚠️ Showing ${result.errors.length} errors...`);
            const errorsDiv = document.getElementById('validationErrors');
            const errorsList = document.getElementById('errorsList');
            
            if (errorsDiv && errorsList) {
                let errorsHtml = '';
                result.errors.slice(0, 10).forEach(error => {
                    errorsHtml += `<li class="text-danger small">${error}</li>`;
                });
                
                if (result.errors.length > 10) {
                    errorsHtml += `<li class="text-muted small">... e mais ${result.errors.length - 10} erros</li>`;
                }
                
                errorsList.innerHTML = errorsHtml;
                errorsDiv.classList.remove('d-none');
            }
        } else {
            console.log('✅ No errors to display');
        }
        
        console.log('✅ displayValidationResults completed');
    }
    
    updateDistributionInfo() {
        const selectedPhones = this.getSelectedPhoneNumbers();
        const selectedTemplates = this.getSelectedTemplates();
        const validLeads = this.leads.length;
        
        const distributionInfo = document.getElementById('distributionInfo');
        const templatesCount = document.getElementById('templatesCount');
        const validLeadsCount = document.getElementById('validLeadsCount');
        
        // Phone numbers count is updated in populatePhoneNumbers
        if (templatesCount) templatesCount.textContent = selectedTemplates.length;
        if (validLeadsCount) validLeadsCount.textContent = validLeads;
        
        if (distributionInfo) {
            if (selectedPhones.length > 0 && selectedTemplates.length > 0 && validLeads > 0) {
                distributionInfo.classList.remove('d-none');
            } else {
                distributionInfo.classList.add('d-none');
            }
        }
        
        // Update send button
        const sendButton = document.getElementById('smartDistributionBtn');
        if (sendButton) {
            sendButton.disabled = !(selectedPhones.length > 0 && selectedTemplates.length > 0 && validLeads > 0);
        }
    }
    
    getSelectedPhoneNumbers() {
        // Return ALL available phone numbers - no selection needed
        if (!this.connectionData || !this.connectionData.phone_numbers) {
            return [];
        }
        
        return this.connectionData.phone_numbers.map(phone => ({
            id: phone.id,
            displayName: phone.display_name || phone.id
        }));
    }
    
    getSelectedTemplates() {
        const checkboxes = document.querySelectorAll('#templatesContainer input[type="checkbox"]:checked');
        const templates = [];
        checkboxes.forEach(checkbox => {
            templates.push({
                name: checkbox.value,
                displayName: checkbox.getAttribute('data-display-name') || checkbox.value
            });
        });
        return templates;
    }
    
    selectAllTemplates() {
        const checkboxes = document.querySelectorAll('#templatesContainer .template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        this.updateDistributionInfo();
        this.updateTemplateButtons();
        this.showAlert('Todos os templates selecionados', 'success');
    }
    
    clearTemplateSelection() {
        const checkboxes = document.querySelectorAll('#templatesContainer .template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateDistributionInfo();
        this.updateTemplateButtons();
        this.showAlert('Seleção de templates limpa', 'info');
    }
    
    updateTemplateButtons() {
        const checkboxes = document.querySelectorAll('#templatesContainer .template-checkbox');
        const checkedCount = document.querySelectorAll('#templatesContainer .template-checkbox:checked').length;
        const totalCount = checkboxes.length;
        
        const selectAllBtn = document.getElementById('selectAllTemplatesBtn');
        const clearBtn = document.getElementById('clearTemplatesBtn');
        
        if (selectAllBtn) selectAllBtn.disabled = totalCount === 0;
        if (clearBtn) clearBtn.disabled = checkedCount === 0;
    }
    
    async sendSmartDistribution() {
        const selectedTemplates = this.getSelectedTemplates();
        const phoneNumbers = this.getSelectedPhoneNumbers();
        
        if (this.leads.length === 0) {
            this.showAlert('Primeiro valide os leads antes de enviar', 'warning');
            return;
        }
        
        if (selectedTemplates.length === 0) {
            this.showAlert('Selecione pelo menos um template', 'warning');
            return;
        }
        
        if (phoneNumbers.length === 0) {
            this.showAlert('Nenhum número de telefone disponível. Conecte-se primeiro.', 'warning');
            return;
        }
        
        // INSTANT START - No confirmation needed
        try {
            // Show progress immediately for instant feedback
            this.showProgressPanel();
            
            const leadsText = this.leads.map(lead => `${lead.numero},${lead.nome},${lead.cpf}`).join('\n');
            
            const requestData = {
                leads: leadsText,
                template_names: selectedTemplates.map(t => t.name),
                phone_number_ids: phoneNumbers.map(p => p.id),
                // CRITICAL: Send connection data
                whatsapp_connection: this.connectionData
            };
            
            const response = await fetch('/api/ultra-speed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showAlert('Envio iniciado com sucesso!', 'success');
                
                // Start progress tracking
                const sessionId = result.session_id;
                this.trackProgress(sessionId);
            } else {
                // Check for specific error types
                if (response.status === 401 || result.error_type === 'expired_token') {
                    this.showAlert('⚠️ TOKEN EXPIRADO: Seu token WhatsApp expirou. Por favor, obtenha um novo token e reconecte.', 'warning');
                    this.disconnect(); // Force disconnect to show connection form
                } else {
                    this.showAlert(result.error || 'Erro ao iniciar envio', 'danger');
                }
            }
            
        } catch (error) {
            console.error('Error sending messages:', error);
            this.showAlert('Erro de conexão com o servidor', 'danger');
        }
    }
    
    trackProgress(sessionId) {
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/progress/${sessionId}`);
                const data = await response.json();
                
                // HEROKU DEBUG: Log API response
                console.log('HEROKU Progress API Response:', data);
                
                if (data.success) {
                    const { sent, total, failed, progress, status } = data;
                    
                    // Update progress bar
                    document.getElementById('progressBar').style.width = `${progress}%`;
                    document.getElementById('progressPercent').textContent = `${progress}%`;
                    
                    // Update counters
                    document.getElementById('sentProgress').textContent = sent;
                    document.getElementById('totalProgress').textContent = total;
                    document.getElementById('successProgress').textContent = sent; // Use sent as success count
                    document.getElementById('errorProgress').textContent = failed;
                    
                    // Update status message
                    document.getElementById('statusMessage').innerHTML = 
                        `<i class="fas fa-rocket text-primary me-2"></i>ULTRA-SPEED: ${sent}/${total} enviadas (${failed} falharam) - ${progress}%`;
                    
                    if (status === 'completed' || progress >= 100) {
                        document.getElementById('statusMessage').innerHTML = 
                            `<i class="fas fa-check-circle text-success me-2"></i>✅ ULTRA-SPEED COMPLETO! ${sent} mensagens enviadas de ${total} (${failed} falharam)`;
                        this.showAlert(`Envio concluído! ${sent} mensagens enviadas de ${total}`, 'success');
                        return;
                    }
                    
                    setTimeout(checkProgress, 250); // Check every 250ms for instant updates
                } else {
                    // Handle any error by continuing to check progress
                    console.warn('Progress API returned error, continuing to check...', data);
                    
                    // Continue checking even on errors - never stop
                    setTimeout(checkProgress, 500); // Check again in 500ms
                }
            } catch (error) {
                console.error('HEROKU Error checking progress:', error);
                document.getElementById('statusMessage').innerHTML = 
                    `<i class="fas fa-wifi text-danger me-2"></i>Erro de conexão com servidor`;
            }
        };
        
        checkProgress();
    }
    
    showProgressPanel() {
        const progressPanel = document.getElementById('progressPanel');
        if (progressPanel) {
            progressPanel.classList.remove('d-none');
            
            // Reset counters
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressPercent').textContent = '0%';
            document.getElementById('sentProgress').textContent = '0';
            document.getElementById('totalProgress').textContent = '0';
            document.getElementById('successProgress').textContent = '0';
            document.getElementById('errorProgress').textContent = '0';
            document.getElementById('statusMessage').innerHTML = 
                '<i class="fas fa-clock text-warning me-2"></i>Iniciando envio ultra-velocidade...';
                
            // Scroll to progress panel
            progressPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    resetValidation() {
        const validationDiv = document.getElementById('leadsValidation');
        if (validationDiv) {
            validationDiv.classList.add('d-none');
        }
        
        this.leads = [];
        this.updateDistributionInfo();
    }
    
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    async testProxy() {
        const proxyConnection = document.getElementById('proxyConnection').value.trim();
        
        if (!proxyConnection) {
            this.showAlert('Digite uma proxy para testar', 'warning');
            return;
        }
        
        // Validate proxy format
        const parts = proxyConnection.split(':');
        if (parts.length < 4) {
            this.showAlert('Formato inválido. Use: host:port:user:password', 'danger');
            return;
        }
        
        const testBtn = document.getElementById('testProxyBtn');
        const originalText = testBtn.innerHTML;
        testBtn.disabled = true;
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testando...';
        
        try {
            // First add the proxy to database temporarily for testing
            const addResponse = await fetch('/api/proxies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'Teste Temporário',
                    proxy_string: proxyConnection
                })
            });
            
            if (addResponse.ok) {
                const addResult = await addResponse.json();
                const proxyId = addResult.proxy.id;
                
                // Test the proxy
                const testResponse = await fetch(`/api/proxies/${proxyId}/test`, {
                    method: 'POST'
                });
                
                const testResult = await testResponse.json();
                
                if (testResult.success) {
                    this.showAlert(`✅ Proxy OK! IP: ${testResult.ip}, Tempo: ${(testResult.response_time * 1000).toFixed(0)}ms`, 'success');
                } else {
                    this.showAlert(`❌ Proxy com problemas: ${testResult.error}`, 'danger');
                }
                
                // Remove temporary proxy
                await fetch(`/api/proxies/${proxyId}`, { method: 'DELETE' });
            } else {
                this.showAlert('Erro ao adicionar proxy temporária para teste', 'danger');
            }
        } catch (error) {
            console.error('Erro ao testar proxy:', error);
            this.showAlert('Erro de conexão ao testar proxy', 'danger');
        } finally {
            testBtn.disabled = false;
            testBtn.innerHTML = originalText;
        }
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.app = new WhatsAppSender();
});