// WhatsApp Sender Application
class WhatsAppSender {
    constructor() {
        this.leads = [];
        this.validationErrors = [];
        this.connectionData = null; // Store connection info
        
        this.initializeEventListeners();
        this.checkSavedConnection(); // Check for saved connection first
        this.loadURLParameters(); // Load leads from URL if present
    }
    
    initializeEventListeners() {
        // Test Z-API button
        const testBtn = document.getElementById('testWhatsAppBtn');
        if (testBtn) {
            testBtn.addEventListener('click', () => {
                this.testWhatsAppConnection();
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
            });
        }
        
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
    }
    
    async loadPhoneNumbers() {
        console.log('Loading phone numbers...');
        
        const businessManagerId = document.getElementById('businessAccountId').value.trim();
        
        if (!businessManagerId) {
            this.showAlert('⚠️ Digite o ID da Business Manager primeiro', 'warning');
            return;
        }
        
        const btn = document.getElementById('loadPhonesBtn');
        const originalText = btn.innerHTML;
        
        btn.classList.add('btn-loading');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Carregando...';
        
        try {
            const response = await fetch(`/api/phone-numbers?business_manager_id=${businessManagerId}`);
            const result = await response.json();
            
            const phoneSelect = document.getElementById('phoneNumberId');
            
            if (result.phone_numbers && result.phone_numbers.length > 0) {
                // Clear existing options
                phoneSelect.innerHTML = '<option value="">Selecione o Phone Number</option>';
                
                // Add phone numbers
                result.phone_numbers.forEach(phone => {
                    const option = document.createElement('option');
                    option.value = phone.id;
                    option.textContent = phone.display_name;
                    phoneSelect.appendChild(option);
                });
                
                console.log(`Loaded ${result.phone_numbers.length} phone numbers from BM ${businessManagerId}`);
                
                // Show success message
                this.showAlert(`✅ ${result.phone_numbers.length} números carregados da BM ${businessManagerId}`, 'success');
                
            } else {
                phoneSelect.innerHTML = '<option value="">Nenhum número disponível</option>';
                this.showAlert('❌ Nenhum número encontrado na BM especificada', 'warning');
            }
            
        } catch (error) {
            console.error('Error loading phone numbers:', error);
            const phoneSelect = document.getElementById('phoneNumberId');
            phoneSelect.innerHTML = '<option value="">Erro ao carregar números</option>';
            this.showAlert('❌ Erro ao carregar números. Verifique o ID da BM', 'danger');
        } finally {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
    
    async testWhatsAppConnection() {
        const btn = document.getElementById('testWhatsAppBtn');
        const originalText = btn.innerHTML;
        
        btn.classList.add('btn-loading');
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/test-whatsapp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            const alertDiv = document.getElementById('apiStatusAlert');
            const messageSpan = document.getElementById('apiStatusMessage');
            
            if (result.success) {
                alertDiv.className = 'alert alert-success';
                messageSpan.innerHTML = `<strong>✅ Sistema Ativo!</strong> ${result.message} - 5 phones disponíveis para seleção`;
                
                // Show success message for credential update
                this.showAlert('🔄 Credenciais carregadas automaticamente das secrets!', 'success');
            } else {
                alertDiv.className = 'alert alert-danger';
                messageSpan.innerHTML = `<strong>❌ Erro:</strong> ${result.error}`;
            }
            
            alertDiv.classList.remove('d-none');
            
            // Hide alert after 5 seconds
            setTimeout(() => {
                alertDiv.classList.add('d-none');
            }, 5000);
            
        } catch (error) {
            console.error('Error testing WhatsApp Business API:', error);
            const alertDiv = document.getElementById('apiStatusAlert');
            const messageSpan = document.getElementById('apiStatusMessage');
            
            alertDiv.className = 'alert alert-danger';
            messageSpan.textContent = 'Erro de conexão com o servidor';
            alertDiv.classList.remove('d-none');
        } finally {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
    
    async validateLeads() {
        const leadsText = document.getElementById('leadsInput').value.trim();
        
        if (!leadsText) {
            this.showAlert('Por favor, insira a lista de leads', 'warning');
            return;
        }
        
        const btn = document.getElementById('validateLeadsBtn');
        const originalText = btn.innerHTML;
        
        btn.classList.add('btn-loading');
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/validate-leads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ leads: leadsText })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.leads = result.leads;
                this.validationErrors = result.errors;
                this.displayValidationResults(result);

            } else {
                this.showAlert(result.error || 'Erro na validação', 'danger');
            }
            
        } catch (error) {
            console.error('Error validating leads:', error);
            this.showAlert('Erro de conexão com o servidor', 'danger');
        } finally {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
    
    displayValidationResults(result) {
        const validationDiv = document.getElementById('leadsValidation');
        
        // Update counters
        document.getElementById('validCount').textContent = result.total_valid;
        document.getElementById('errorCount').textContent = result.total_errors;
        document.getElementById('totalCount').textContent = result.original_count || (result.total_valid + result.total_errors);
        
        // Show duplicate filter information if present
        if (result.filtered_count > 0) {
            const duplicateInfo = document.createElement('div');
            duplicateInfo.className = 'alert alert-info mt-2';
            duplicateInfo.innerHTML = `
                <i class="fas fa-filter me-2"></i>
                <strong>Filtro Anti-Duplicação:</strong> ${result.filtered_count} leads removidos (já foram enviados anteriormente).
                ${result.already_sent && result.already_sent.length > 0 ? 
                    `<div class="mt-2"><small>Exemplos: ${result.already_sent.slice(0, 3).map(lead => `${lead.nome} (${lead.numero})`).join(', ')}</small></div>` : ''}
            `;
            
            // Remove any existing duplicate info
            const existingInfo = validationDiv.querySelector('.alert-info');
            if (existingInfo) {
                existingInfo.remove();
            }
            
            validationDiv.appendChild(duplicateInfo);
        }
        
        // Show/hide errors
        const errorsDiv = document.getElementById('validationErrors');
        const errorsList = document.getElementById('errorsList');
        
        if (result.errors.length > 0) {
            errorsList.innerHTML = result.errors
                .map(error => `<li class="error-item">${error}</li>`)
                .join('');
            errorsDiv.classList.remove('d-none');
        } else {
            errorsDiv.classList.add('d-none');
        }
        
        validationDiv.classList.remove('d-none');
        validationDiv.classList.add('fade-in');
        
        // Update smart distribution info
        this.updateDistributionInfo(result.total_valid);
        
        // Show appropriate alert message
        if (result.summary) {
            const alertType = result.filtered_count > 0 ? 'info' : 'success';
            this.showAlert(result.summary, alertType);
        } else if (result.total_valid > 0) {
            this.showAlert(`✅ ${result.total_valid} leads válidos encontrados!`, 'success');
        }
    }
    
    resetValidation() {
        document.getElementById('leadsValidation').classList.add('d-none');
        document.getElementById('distributionInfo').classList.add('d-none');
        document.getElementById('smartDistributionBtn').disabled = true;
        this.leads = [];
        this.validationErrors = [];
    }
    
    updateDistributionInfo(validLeadsCount = null) {
        const distributionInfo = document.getElementById('distributionInfo');
        const smartBtn = document.getElementById('smartDistributionBtn');
        
        const totalValid = validLeadsCount || this.leads.length;
        const phoneNumbers = this.getAvailablePhoneNumbers();
        const selectedTemplates = this.getSelectedTemplates();
        
        if (totalValid > 0 && phoneNumbers.length > 0 && selectedTemplates.length > 0) {
            // Update info display
            document.getElementById('phoneNumbersCount').textContent = phoneNumbers.length;
            document.getElementById('templatesCount').textContent = selectedTemplates.length;
            document.getElementById('validLeadsCount').textContent = totalValid;
            
            // Show info and enable button
            distributionInfo.classList.remove('d-none');
            smartBtn.disabled = false;
            
            // Update distribution preview
            this.updateDistributionPreview(totalValid, phoneNumbers.length, selectedTemplates.length);
        } else {
            // Hide info and disable button
            distributionInfo.classList.add('d-none');
            smartBtn.disabled = true;
        }
    }
    
    updateDistributionPreview(totalLeads, phoneCount, templateCount) {
        const previewDiv = document.getElementById('distributionPreview');
        const detailsDiv = document.getElementById('distributionDetails');
        
        if (totalLeads > 0 && phoneCount > 0 && templateCount > 0) {
            const leadsPerPhone = Math.ceil(totalLeads / phoneCount);
            const leadsPerTemplate = Math.ceil(totalLeads / templateCount);
            const estimatedTime = Math.ceil((totalLeads / phoneCount) / 20); // ~20 messages per minute per phone
            
            const estimatedWorkers = phoneCount * templateCount * 50; // 50x multiplier for maximum speed
            const ultraSpeed = Math.round(estimatedWorkers * 10); // MAXIMUM speed: 10 messages per worker per minute
            
            detailsDiv.innerHTML = `
                <div class="row small">
                    <div class="col-6">
                        <strong>📱 Por Número:</strong> ~${Math.min(leadsPerPhone, 1000)} leads<br>
                        <strong>📋 Por Template:</strong> ~${leadsPerTemplate} leads
                    </div>
                    <div class="col-6">
                        <strong>⚡ Workers:</strong> ${estimatedWorkers} paralelos<br>
                        <strong>🚀 MÁXIMA VELOCIDADE:</strong> ~${ultraSpeed} msg/min
                    </div>
                </div>
                <div class="row small mt-2">
                    <div class="col-12 text-center">
                        <span class="badge bg-warning">⚠️ MÁXIMA VELOCIDADE - Templates podem ser banidos rapidamente</span>
                    </div>
                </div>
            `;
            previewDiv.classList.remove('d-none');
        } else {
            previewDiv.classList.add('d-none');
        }
    }
    
    getAvailablePhoneNumbers() {
        const phoneSelect = document.getElementById('phoneNumberId');
        const phones = [];
        for (let option of phoneSelect.options) {
            if (option.value && option.value !== '') {
                phones.push({
                    id: option.value,
                    name: option.textContent
                });
            }
        }
        return phones;
    }
    
    getSelectedTemplates() {
        const templateCheckboxes = document.querySelectorAll('#templatesContainer input[type="checkbox"]:checked');
        const templates = [];
        templateCheckboxes.forEach(checkbox => {
            templates.push({
                name: checkbox.value,
                displayName: checkbox.getAttribute('data-display-name') || checkbox.value
            });
        });
        return templates;
    }
    
    updateTemplateButtons() {
        const checkboxes = document.querySelectorAll('#templatesContainer .template-checkbox');
        const checkedCount = document.querySelectorAll('#templatesContainer .template-checkbox:checked').length;
        const totalCount = checkboxes.length;
        
        document.getElementById('selectAllTemplatesBtn').disabled = totalCount === 0;
        document.getElementById('clearTemplatesBtn').disabled = checkedCount === 0;
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
    
    async sendSmartDistribution() {
        const selectedTemplates = this.getSelectedTemplates();
        const phoneNumbers = this.getAvailablePhoneNumbers();
        
        console.log('DEBUG: Selected templates:', selectedTemplates);
        console.log('DEBUG: Available phone numbers:', phoneNumbers);
        console.log('DEBUG: Leads count:', this.leads.length);
        
        if (this.leads.length === 0) {
            this.showAlert('Primeiro valide os leads antes de enviar', 'warning');
            return;
        }
        
        if (selectedTemplates.length === 0) {
            this.showAlert('Selecione pelo menos um template', 'warning');
            return;
        }
        
        if (phoneNumbers.length === 0) {
            this.showAlert('Nenhum número de telefone disponível', 'warning');
            return;
        }
        
        const estimatedWorkers = phoneNumbers.length * selectedTemplates.length * 50; // MAXIMUM speed configuration
        
        const confirmMessage = `🚀 DISTRIBUIÇÃO ULTRA-RÁPIDA
        
📊 Resumo:
• ${this.leads.length} leads válidos
• ${phoneNumbers.length} números de telefone
• ${selectedTemplates.length} templates selecionados

⚡ Sistema ULTRA-SPEED:
• Distribuir máximo 1000 leads por número
• ${estimatedWorkers} workers paralelos (como ${estimatedWorkers} abas)
• Envio simultâneo para máxima velocidade
• Evitar banimento por sobrecarga de templates

⚠️ AVISO: Sistema otimizado para velocidade máxima!
Templates e números podem ser banidos rapidamente.

Confirmar envio ULTRA-RÁPIDO?`;

        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            this.showProgressPanel();
            document.getElementById('statusMessage').innerHTML = '<i class="fas fa-rocket text-danger me-2"></i>Iniciando Distribuição ULTRA-RÁPIDA...';
            
            const leadsText = this.leads.map(lead => `${lead.numero},${lead.nome},${lead.cpf}`).join('\n');
            
            const requestData = {
                leads: leadsText,
                template_names: selectedTemplates.map(t => t.name),
                phone_number_ids: phoneNumbers.map(p => p.id)
            };
            
            console.log('DEBUG: Sending request data:', requestData);
            
            const response = await fetch('/api/ultra-speed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            console.log('DEBUG: Ultra-speed response:', result);
            
            if (response.ok && result.success) {
                this.showAlert('🚀 ULTRA-SPEED FUNCIONANDO! Mensagens sendo enviadas em máxima velocidade!', 'success');
                
                // Start real-time progress tracking
                const sessionId = result.session_id;
                let progressInterval;
                
                const checkProgress = async () => {
                    try {
                        const progressResponse = await fetch(`/api/progress/${sessionId}`);
                        const progressData = await progressResponse.json();
                        
                        if (progressData.success) {
                            const { sent, total, failed, progress, status } = progressData;
                            
                            document.getElementById('statusMessage').innerHTML = 
                                `<i class="fas fa-rocket text-success me-2"></i>ULTRA-SPEED: ${sent}/${total} enviadas (${failed} falharam) - ${progress}%`;
                            
                            if (status === 'completed' || progress >= 100) {
                                clearInterval(progressInterval);
                                document.getElementById('statusMessage').innerHTML = 
                                    `<i class="fas fa-trophy text-warning me-2"></i>ULTRA-SPEED COMPLETO! ${sent} mensagens enviadas de ${total} (${failed} falharam)`;
                                setTimeout(() => {
                                    document.getElementById('progressPanel').style.display = 'none';
                                }, 3000);
                            }
                        }
                    } catch (error) {
                        console.error('Error checking progress:', error);
                    }
                };
                
                // Check progress every 500ms for real-time updates
                progressInterval = setInterval(checkProgress, 500);
                // Initial check
                checkProgress();
            } else {
                this.showAlert(result.error || 'Erro ao iniciar ultra-velocidade', 'danger');
                document.getElementById('progressPanel').style.display = 'none';
            }
            
        } catch (error) {
            console.error('Error sending smart distribution:', error);
            this.showAlert('Erro de conexão ao iniciar distribuição', 'danger');
            document.getElementById('progressPanel').style.display = 'none';
        }
    }

    loadURLParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const leads = urlParams.get('leads');
        const tab = urlParams.get('tab');
        const total = urlParams.get('total');
        
        if (leads && tab && total) {
            // Decode and load leads into textarea
            const decodedLeads = decodeURIComponent(leads);
            document.getElementById('leadsInput').value = decodedLeads;
            
            // Update page title to show tab info
            document.title = `Aba ${tab}/${total} - Sistema WhatsApp MEGA LOTE`;
            
            // Add tab info to header
            const header = document.querySelector('h1');
            if (header) {
                header.innerHTML = `
                    <i class="fab fa-whatsapp text-success me-2"></i>
                    Sistema WhatsApp - Aba ${tab}/${total}
                    <small class="badge bg-primary ms-2">AUTO LOTE</small>
                `;
            }
            
            // Auto-validate leads
            setTimeout(() => {
                this.validateLeads();
            }, 1000);
            
            // Show auto-loaded message
            this.showAlert(`Aba ${tab}/${total} carregada automaticamente com leads! Validando leads...`, 'info');
        }
    }


    
    updateSendButton() {
        const sendBtn = document.getElementById('sendBtn');
        const megaBatchBtn = document.getElementById('megaBatchBtn');
        const templateSelect = document.getElementById('templateSelect');
        
        const canSend = this.leads.length > 0 && 
                       templateSelect.value.trim();
        
        sendBtn.disabled = !canSend;
        megaBatchBtn.disabled = !canSend;
    }
    
    async sendMessages() {
        const templateName = document.getElementById('templateSelect').value.trim();
        
        if (!this.leads.length || !templateName) {
            this.showAlert('Dados incompletos para envio', 'warning');
            return;
        }
        
        const btn = document.getElementById('sendBtn');
        const originalText = btn.innerHTML;
        
        btn.classList.add('btn-loading');
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/send-instant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    leads: this.leads,
                    template_name: templateName
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showAlert(`🔄 ENVIO COM AUTO-RETRY iniciado para ${result.total_leads} leads! Sistema com retomada automática em caso de erro.`, 'success');
                
                // Show ultra-fast mode indicator
                const progressPanel = document.getElementById('progressPanel');
                progressPanel.classList.remove('d-none');
                document.getElementById('progressTitle').textContent = '🔄 Modo Auto-Retry - Sistema Inteligente';
                document.getElementById('progressBar').style.width = '0%';
                document.getElementById('progressText').textContent = `Iniciando sistema com retry automático para ${result.total_leads} mensagens...`;
                
                // Real-time progress tracking
                let currentBatch = 0;
                const totalBatches = Math.ceil(result.total_leads / 50);
                let progressUpdateCount = 0;
                
                const updateProgress = () => {
                    progressUpdateCount++;
                    currentBatch = Math.min(progressUpdateCount, totalBatches);
                    const progress = Math.min((currentBatch / totalBatches) * 100, 100);
                    
                    document.getElementById('progressBar').style.width = `${progress}%`;
                    document.getElementById('progressText').textContent = `Lote ${currentBatch}/${totalBatches} - ${Math.round(progress)}% concluído (${Math.min(currentBatch * 50, result.total_leads)} mensagens)`;
                    
                    if (currentBatch < totalBatches) {
                        setTimeout(updateProgress, 2500); // Update every 2.5 seconds
                    } else {
                        // Final completion check
                        setTimeout(() => {
                            document.getElementById('progressBar').style.width = '100%';
                            document.getElementById('progressText').textContent = `Concluído! ${result.total_leads} mensagens processadas com sucesso`;
                            btn.disabled = false;
                            btn.classList.remove('btn-loading');
                            this.showAlert('✅ Envio com auto-retry concluído! Sistema processou todas as mensagens com retomada automática.', 'success');
                        }, 3000);
                    }
                };
                
                // Start progress updates after 2 seconds
                setTimeout(updateProgress, 2000);
            } else {
                this.showAlert(result.error || 'Erro ao iniciar envio', 'danger');
            }
            
        } catch (error) {
            console.error('Error sending messages:', error);
            this.showAlert('Erro de conexão com o servidor', 'danger');
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
    
    showProgressPanel() {
        const progressPanel = document.getElementById('progressPanel');
        progressPanel.classList.remove('d-none');
        progressPanel.classList.add('fade-in');
        
        // Scroll to progress panel
        progressPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    

    
    updateProgressDisplay(status) {
        // Update progress bar
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        progressBar.style.width = `${status.progress}%`;
        progressPercent.textContent = `${status.progress}%`;
        
        // Update counters
        document.getElementById('totalProgress').textContent = status.total_leads;
        document.getElementById('sentProgress').textContent = status.sent_count;
        document.getElementById('successProgress').textContent = status.success_count;
        document.getElementById('errorProgress').textContent = status.error_count;
        
        // Update status message
        const statusMessage = document.getElementById('statusMessage');
        switch (status.status) {
            case 'pending':
                statusMessage.innerHTML = '<i class="fas fa-clock text-warning me-2"></i>Preparando envio...';
                break;
            case 'sending':
                statusMessage.innerHTML = '<i class="fas fa-paper-plane text-primary me-2"></i>Enviando mensagens...';
                break;
            case 'completed':
                statusMessage.innerHTML = '<i class="fas fa-check-circle text-success me-2"></i>Envio concluído!';
                break;
            case 'failed':
                statusMessage.innerHTML = '<i class="fas fa-exclamation-circle text-danger me-2"></i>Erro no envio';
                break;
        }
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async sendMegaBatch() {
        const leadsText = document.getElementById('leadsInput').value.trim();
        const templateName = document.getElementById('templateSelect').value.trim();
        const phoneNumberId = document.getElementById('phoneNumberId').value.trim();
        
        if (!leadsText || !templateName) {
            this.showAlert('Por favor, preencha os leads e selecione um template', 'warning');
            return;
        }
        
        if (!phoneNumberId) {
            this.showAlert('Por favor, selecione um Phone Number ID', 'warning');
            return;
        }

        if (!confirm(`MEGA LOTE: Processar ${this.leads.length} leads em lotes de 20 com limpeza de memória?\n\nEste modo é otimizado para listas grandes (5000+) e fará:\n• Processamento em batches de 20\n• Limpeza de memória entre lotes\n• Resumo automático em caso de erro\n• Progresso salvo para retomada`)) {
            return;
        }

        try {
            this.showProgressPanel();
            document.getElementById('statusMessage').innerHTML = '<i class="fas fa-rocket text-primary me-2"></i>Iniciando MEGA LOTE...';
            
            const response = await fetch('/api/send-mega-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    leads: leadsText,
                    template_name: templateName,
                    phone_number_id: phoneNumberId
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showAlert(`MEGA LOTE iniciado! ${data.total_leads} leads serão processados em ${data.estimated_batches} lotes`, 'success');
                this.startBatchStatusChecking();
            } else {
                this.showAlert(data.error || 'Erro ao iniciar MEGA LOTE', 'danger');
            }
            
        } catch (error) {
            console.error('Error sending mega batch:', error);
            this.showAlert('Erro de conexão', 'danger');
        }
    }

    startBatchStatusChecking() {
        // Clear any existing interval
        if (this.batchStatusInterval) {
            clearInterval(this.batchStatusInterval);
        }
        
        // Start checking batch status immediately and then every 1 second
        this.checkBatchStatus(); // First check immediately
        this.batchStatusInterval = setInterval(() => {
            this.checkBatchStatus();
        }, 1000); // Check every 1 second for faster updates
    }

    async checkBatchStatus() {
        try {
            const response = await fetch('/api/batch-status');
            const status = await response.json();
            
            if (response.ok) {
                this.updateBatchProgressDisplay(status);
                
                // Stop checking if not running
                if (!status.is_running && status.processed > 0) {
                    clearInterval(this.batchStatusInterval);
                    this.batchStatusInterval = null;
                    
                    if (status.processed === status.total_leads) {
                        this.showAlert('MEGA LOTE concluído com sucesso!', 'success');
                        document.getElementById('statusMessage').innerHTML = '<i class="fas fa-check-circle text-success me-2"></i>MEGA LOTE concluído!';
                    }
                }
            }
        } catch (error) {
            console.error('Error checking batch status:', error);
        }
    }

    updateBatchProgressDisplay(status) {
        // Update progress bar
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        // Use the calculated progress from backend
        const progress = status.progress_percent || 0;
        
        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
        
        // Update counters
        document.getElementById('totalProgress').textContent = status.total_leads || 0;
        document.getElementById('sentProgress').textContent = status.processed || 0;
        document.getElementById('successProgress').textContent = status.success || 0;
        document.getElementById('errorProgress').textContent = status.errors || 0;
        
        // Update status message
        const statusMessage = document.getElementById('statusMessage');
        if (status.is_running) {
            statusMessage.innerHTML = `<i class="fas fa-rocket text-primary me-2"></i>MEGA LOTE: Processando lote ${status.current_batch}/${status.total_batches} (${status.processed}/${status.total_leads})`;
        } else if (status.processed > 0) {
            statusMessage.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i>✅ MEGA LOTE CONCLUÍDO! ${status.success} sucessos, ${status.errors} erros de ${status.total_leads} total`;
            
            // Stop checking after completion
            if (this.batchStatusInterval) {
                clearInterval(this.batchStatusInterval);
                this.batchStatusInterval = null;
            }
        } else {
            statusMessage.innerHTML = '<i class="fas fa-info-circle text-info me-2"></i>Preparando envio...';
        }
    }

    async stopMegaBatch() {
        try {
            const response = await fetch('/api/stop-batch', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('MEGA LOTE será interrompido após o lote atual', 'warning');
                if (this.batchStatusInterval) {
                    clearInterval(this.batchStatusInterval);
                    this.batchStatusInterval = null;
                }
            } else {
                this.showAlert(data.error || 'Erro ao parar MEGA LOTE', 'danger');
            }
        } catch (error) {
            this.showAlert('Erro de conexão ao parar MEGA LOTE', 'danger');
        }
    }
    
    updateTemplateButtons() {
        const checkboxes = document.querySelectorAll('.template-checkbox');
        const selectAllBtn = document.getElementById('selectAllTemplatesBtn');
        const clearBtn = document.getElementById('clearTemplatesBtn');
        
        const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
        const totalCount = checkboxes.length;
        
        // Enable/disable buttons based on selection
        selectAllBtn.disabled = (checkedCount === totalCount || totalCount === 0);
        clearBtn.disabled = (checkedCount === 0);
        
        // Update distribution info whenever templates change
        this.updateDistributionInfo();
    }
    
    selectAllTemplates() {
        const checkboxes = document.querySelectorAll('.template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        this.updateTemplateButtons();
    }
    
    clearTemplateSelection() {
        const checkboxes = document.querySelectorAll('.template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateTemplateButtons();
    }
    
    getSelectedTemplates() {
        const checkboxes = document.querySelectorAll('.template-checkbox:checked');
        return Array.from(checkboxes).map(checkbox => ({
            name: checkbox.value,
            display_name: checkbox.dataset.displayName
        }));
    }
    
    getAvailablePhoneNumbers() {
        const phoneSelect = document.getElementById('phoneNumberId');
        const phoneNumbers = [];
        
        // Get all phone numbers from the select options (except first placeholder)
        for (let i = 1; i < phoneSelect.options.length; i++) {
            const option = phoneSelect.options[i];
            if (option.value) {
                phoneNumbers.push({
                    id: option.value,
                    display_name: option.textContent
                });
            }
        }
        
        return phoneNumbers;
    }
    
    async autoLoadTemplates() {
        // Auto-load templates if Business Manager ID is available
        const businessAccountId = document.getElementById('businessAccountId').value.trim();
        if (businessAccountId && businessAccountId.length > 5) {
            console.log('Auto-loading templates for BM:', businessAccountId);
            await this.loadAvailableTemplates();
            
            // Auto-select the ricardo template if available
            setTimeout(() => {
                const ricardoCheckbox = document.querySelector('input[value="ricardo_template_1753490810_b7ac4671"]');
                if (ricardoCheckbox) {
                    ricardoCheckbox.checked = true;
                    this.updateDistributionInfo();
                    this.updateTemplateButtons();
                    console.log('Auto-selected ricardo template');
                }
            }, 500);
        }
    }
    
    async loadAvailableTemplates() {
        const container = document.getElementById('templatesContainer');
        const refreshBtn = document.getElementById('refreshTemplatesBtn');
        const loadBtn = document.getElementById('loadTemplatesBtn');
        const businessAccountId = document.getElementById('businessAccountId').value.trim();
        
        if (!businessAccountId) {
            this.showAlert('⚠️ Digite o ID da Business Manager primeiro', 'warning');
            return;
        }
        
        // Show loading state
        container.innerHTML = '<div class="text-center py-3"><i class="fas fa-spinner fa-spin me-2"></i>Carregando templates...</div>';
        refreshBtn.disabled = true;
        loadBtn.disabled = true;
        loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Carregando...';
        
        try {
            const response = await fetch('/api/get-templates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    business_account_id: businessAccountId
                })
            });
            const result = await response.json();
            
            if (result.success) {
                if (result.templates && result.templates.length > 0) {
                    // Create checkboxes for template selection
                    const templatesHtml = result.templates
                        .filter(template => template.name !== 'template_discovery_info')
                        .map(template => {
                            const displayName = `${template.name} (${template.language}) - ${template.category}`;
                            const features = [];
                            if (template.has_parameters) features.push('parâmetros');
                            if (template.has_buttons) features.push('botões');
                            const featureText = features.length > 0 ? ` [${features.join(', ')}]` : '';
                            
                            return `
                                <div class="form-check mb-2">
                                    <input class="form-check-input template-checkbox" type="checkbox" 
                                           value="${template.name}" id="template_${template.name}"
                                           data-display-name="${displayName}${featureText}">
                                    <label class="form-check-label" for="template_${template.name}">
                                        <strong>${template.name}</strong><br>
                                        <small class="text-muted">${template.language} - ${template.category}${featureText}</small>
                                    </label>
                                </div>
                            `;
                        })
                        .join('');
                    
                    container.innerHTML = templatesHtml;
                    
                    // Add event listeners to checkboxes
                    const checkboxes = container.querySelectorAll('.template-checkbox');
                    checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', () => {
                            this.updateDistributionInfo();
                            this.updateTemplateButtons();
                        });
                    });
                    
                    this.updateTemplateButtons();
                    this.showAlert(`${result.templates.length} templates carregados da conta WhatsApp Business`, 'success');
                } else {
                    container.innerHTML = '<div class="text-muted text-center py-3">Nenhum template encontrado</div>';
                    this.showAlert('Para buscar templates automaticamente, configure WHATSAPP_BUSINESS_ACCOUNT_ID nas secrets', 'info');
                }
            } else {
                container.innerHTML = '<div class="text-danger text-center py-3">Erro ao carregar templates</div>';
                this.showAlert('Erro ao carregar templates da conta', 'danger');
            }
        } catch (error) {
            console.error('Error loading templates:', error);
            container.innerHTML = '<div class="text-danger text-center py-3">Erro de conexão</div>';
            this.showAlert('Erro de conexão ao carregar templates', 'danger');
        } finally {
            refreshBtn.disabled = false;
            loadBtn.disabled = false;
            loadBtn.innerHTML = '<i class="fas fa-file-alt me-1"></i>Templates';
        }
    }
    
    async loadLastBusinessManagerId() {
        try {
            const response = await fetch('/api/get-business-manager-id');
            const result = await response.json();
            
            if (result.business_manager_id) {
                document.getElementById('businessAccountId').value = result.business_manager_id;
                console.log('Business Manager ID carregado da sessão:', result.business_manager_id);
                // Auto-load templates after BM ID is loaded
                setTimeout(() => {
                    this.autoLoadTemplates();
                }, 1000);
            }
        } catch (error) {
            console.error('Erro ao carregar Business Manager ID:', error);
        }
    }
    
    async saveBusinessManagerId(bmId) {
        try {
            await fetch('/api/save-business-manager-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    business_manager_id: bmId
                })
            });
            console.log('Business Manager ID salvo na sessão:', bmId);
        } catch (error) {
            console.error('Erro ao salvar Business Manager ID:', error);
        }
    }
    
    async discoverPhoneNumbersFromToken() {
        try {
            // Tentar descobrir automaticamente phone numbers baseado no token configurado
            const response = await fetch('/api/discover-phones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.business_manager_id) {
                    // Preencher automaticamente o Business Manager ID descoberto
                    document.getElementById('businessAccountId').value = result.business_manager_id;
                    this.saveBusinessManagerId(result.business_manager_id);
                    console.log('Business Manager ID descoberto automaticamente:', result.business_manager_id);
                }
            }
        } catch (error) {
            console.error('Erro ao descobrir phone numbers automaticamente:', error);
        }
    }
    
    // ========== CONNECTION FUNCTIONS ==========
    
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
    
    async connectWhatsApp() {
        const accessToken = document.getElementById('accessToken').value.trim();
        const businessManagerId = document.getElementById('businessManagerId').value.trim();
        
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
                    business_manager_id: businessManagerId || null
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.connectionData = result.data;
                
                // Salvar conexão no localStorage
                localStorage.setItem('whatsapp_connection', JSON.stringify(this.connectionData));
                
                this.updateConnectionUI(true);
                this.loadConnectionData();
                
                this.showAlert('Conectado com sucesso! Carregando dados...', 'success');
            } else {
                this.showAlert(result.message || 'Erro ao conectar', 'danger');
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
            
            // Popular números e templates nas seções de configuração
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
            this.clearPhoneNumbers();
            this.clearTemplates();
        }
    }
    
    populatePhoneNumbers(phoneNumbers) {
        const phoneNumbersContainer = document.getElementById('phoneNumbersContainer');
        
        if (!phoneNumbers || phoneNumbers.length === 0) {
            phoneNumbersContainer.innerHTML = `
                <div class="text-muted text-center py-2">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    Nenhum número encontrado na conta
                </div>
            `;
            return;
        }
        
        let html = '';
        phoneNumbers.forEach(phone => {
            const qualityBadgeClass = phone.quality_rating === 'GREEN' ? 'bg-success' : 
                                    phone.quality_rating === 'YELLOW' ? 'bg-warning' : 'bg-secondary';
            
            html += `
                <div class="form-check d-flex align-items-center justify-content-between mb-2">
                    <div>
                        <input class="form-check-input phone-checkbox" type="checkbox" value="${phone.id}" id="phone_${phone.id}">
                        <label class="form-check-label ms-2" for="phone_${phone.id}">
                            <strong>${phone.display_phone_number}</strong>
                            ${phone.verified_name ? `<br><small class="text-muted">${phone.verified_name}</small>` : ''}
                        </label>
                    </div>
                    <span class="badge ${qualityBadgeClass}">${phone.quality_rating}</span>
                </div>
            `;
        });
        
        phoneNumbersContainer.innerHTML = html;
        this.addPhoneNumberEventListeners();
    }
    
    populateTemplates(templates) {
        const templatesContainer = document.getElementById('templatesContainer');
        
        if (!templates || templates.length === 0) {
            templatesContainer.innerHTML = `
                <div class="text-muted text-center py-2">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    Nenhum template aprovado encontrado
                </div>
            `;
            document.getElementById('selectAllTemplatesBtn').disabled = true;
            document.getElementById('clearTemplatesBtn').disabled = true;
            return;
        }
        
        let html = '';
        templates.forEach(template => {
            const categoryBadgeClass = template.category === 'MARKETING' ? 'bg-primary' : 
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
                        <span class="badge ${categoryBadgeClass} me-1">${template.category}</span>
                        ${template.has_buttons ? '<i class="fas fa-link text-primary" title="Tem botões"></i>' : ''}
                        ${template.has_parameters ? '<i class="fas fa-code text-info" title="Tem parâmetros"></i>' : ''}
                    </div>
                </div>
            `;
        });
        
        templatesContainer.innerHTML = html;
        document.getElementById('selectAllTemplatesBtn').disabled = false;
        document.getElementById('clearTemplatesBtn').disabled = false;
        this.addTemplateEventListeners();
    }
    
    addPhoneNumberEventListeners() {
        const checkboxes = document.querySelectorAll('.phone-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
            });
        });
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
    
    clearPhoneNumbers() {
        const phoneNumbersContainer = document.getElementById('phoneNumbersContainer');
        phoneNumbersContainer.innerHTML = `
            <div class="text-muted text-center py-2">
                <i class="fas fa-plug me-1"></i>
                Conecte-se primeiro para ver os números disponíveis
            </div>
        `;
    }
    
    clearTemplates() {
        const templatesContainer = document.getElementById('templatesContainer');
        templatesContainer.innerHTML = `
            <div class="text-muted text-center py-2">
                <i class="fas fa-plug me-1"></i>
                Conecte-se primeiro para ver os templates disponíveis
            </div>
        `;
        document.getElementById('selectAllTemplatesBtn').disabled = true;
        document.getElementById('clearTemplatesBtn').disabled = true;
    }
    
    clearConnectionData() {
        this.clearPhoneNumbers();
        this.clearTemplates();
    }
    
    loadConnectionData() {
        if (this.connectionData) {
            console.log(`${this.connectionData.phone_numbers.length} phone numbers carregados da conexão`);
            this.updateDistributionInfo();
        }
    }
    
    updateDistributionInfo() {
        const selectedPhones = this.getSelectedPhoneNumbers();
        const selectedTemplates = this.getSelectedTemplates();
        const validLeads = this.leads.length;
        
        const distributionInfo = document.getElementById('distributionInfo');
        const phoneNumbersCount = document.getElementById('phoneNumbersCount');
        const templatesCount = document.getElementById('templatesCount');
        const validLeadsCount = document.getElementById('validLeadsCount');
        
        if (phoneNumbersCount) phoneNumbersCount.textContent = selectedPhones.length;
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
        const checkboxes = document.querySelectorAll('.phone-checkbox:checked');
        const phones = [];
        checkboxes.forEach(checkbox => {
            phones.push({
                id: checkbox.value,
                displayName: checkbox.nextElementSibling.textContent.trim()
            });
        });
        return phones;
    }
    
    getAvailablePhoneNumbers() {
        return this.getSelectedPhoneNumbers();
    }
    
    resetValidation() {
        const validationDiv = document.getElementById('leadsValidation');
        if (validationDiv) {
            validationDiv.classList.add('d-none');
        }
        
        this.leads = [];
        this.updateDistributionInfo();
    }
}
    
    clearPhoneNumbers() {
        const phoneNumbersContainer = document.getElementById('phoneNumbersContainer');
        phoneNumbersContainer.innerHTML = `
            <div class="text-muted text-center py-2">
                <i class="fas fa-plug me-1"></i>
                Conecte-se primeiro para ver os números disponíveis
            </div>
        `;
    }
    
    clearTemplates() {
        const templatesContainer = document.getElementById('templatesContainer');
        templatesContainer.innerHTML = `
            <div class="text-muted text-center py-2">
                <i class="fas fa-plug me-1"></i>
                Conecte-se primeiro para ver os templates disponíveis
            </div>
        `;
        document.getElementById('selectAllTemplatesBtn').disabled = true;
        document.getElementById('clearTemplatesBtn').disabled = true;
    }
    
    addPhoneNumberEventListeners() {
        const phoneCheckboxes = document.querySelectorAll('.phone-checkbox');
        phoneCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
            });
        });
    }
    
    addTemplateEventListeners() {
        const templateCheckboxes = document.querySelectorAll('.template-checkbox');
        templateCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
            });
        });
    }
    
    loadConnectionData() {
        if (!this.connectionData) return;
        
        // Carregar phone numbers
        this.loadPhoneNumbersFromConnection();
        
        // Carregar templates
        this.loadTemplatesFromConnection();
        
        // Salvar BM ID na sessão
        this.saveBusinessManagerId(this.connectionData.business_manager_id);
        
        // Atualizar campo BM ID (se existir)
        const bmField = document.getElementById('businessAccountId');
        if (bmField) {
            bmField.value = this.connectionData.business_manager_id;
        }
    }
    
    loadPhoneNumbersFromConnection() {
        if (!this.connectionData || !this.connectionData.phone_numbers) return;
        
        const container = document.getElementById('phoneNumbersContainer');
        if (!container) return;
        
        const phonesHtml = this.connectionData.phone_numbers.map(phone => {
            return `
                <div class="form-check mb-2">
                    <input class="form-check-input phone-checkbox" type="checkbox" 
                           value="${phone.id}" id="phone_${phone.id}">
                    <label class="form-check-label" for="phone_${phone.id}">
                        <strong>${phone.display_phone_number}</strong><br>
                        <small class="text-muted">Quality: ${phone.quality_rating || 'UNKNOWN'}</small>
                    </label>
                </div>
            `;
        }).join('');
        
        container.innerHTML = phonesHtml;
        
        // Add event listeners
        const checkboxes = container.querySelectorAll('.phone-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
            });
        });
        
        console.log(`${this.connectionData.phone_numbers.length} phone numbers carregados da conexão`);
    }
    
    loadTemplatesFromConnection() {
        if (!this.connectionData || !this.connectionData.templates) return;
        
        const container = document.getElementById('templatesContainer');
        if (!container) return;
        
        const templatesHtml = this.connectionData.templates
            .filter(template => template.status === 'APPROVED')
            .map(template => {
                const features = [];
                if (template.has_parameters) features.push('parâmetros');
                if (template.has_buttons) features.push('botões');
                const featureText = features.length > 0 ? ` [${features.join(', ')}]` : '';
                
                return `
                    <div class="form-check mb-2">
                        <input class="form-check-input template-checkbox" type="checkbox" 
                               value="${template.name}" id="template_${template.name}">
                        <label class="form-check-label" for="template_${template.name}">
                            <strong>${template.name}</strong><br>
                            <small class="text-muted">${template.language} - ${template.category}${featureText}</small>
                        </label>
                    </div>
                `;
            }).join('');
        
        container.innerHTML = templatesHtml;
        
        // Add event listeners
        const checkboxes = container.querySelectorAll('.template-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDistributionInfo();
                this.updateTemplateButtons();
            });
        });
        
        this.updateTemplateButtons();
        console.log(`${this.connectionData.templates.length} templates carregados da conexão`);
    }
    
    clearConnectionData() {
        // Limpar phone numbers
        const phoneContainer = document.getElementById('phoneNumbersContainer');
        if (phoneContainer) {
            phoneContainer.innerHTML = '<div class="text-muted text-center py-3">Conecte-se primeiro para ver os números</div>';
        }
        
        // Limpar templates
        const templateContainer = document.getElementById('templatesContainer');
        if (templateContainer) {
            templateContainer.innerHTML = '<div class="text-muted text-center py-3">Conecte-se primeiro para ver os templates</div>';
        }
        
        // Limpar campo BM ID
        const bmField = document.getElementById('businessAccountId');
        if (bmField) {
            bmField.value = '';
        }
    }
    

    

    

}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.whatsappSender = new WhatsAppSender();
});

// Global functions for HTML onclick events
function connectWhatsApp() {
    if (window.whatsappSender) {
        window.whatsappSender.connectWhatsApp();
    }
}

function disconnect() {
    if (window.whatsappSender) {
        window.whatsappSender.disconnect();
    }
}
