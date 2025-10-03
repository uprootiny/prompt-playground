// API Configuration
const API_BASE_URL = window.location.origin;

// State
let templates = {};
let selectedTemplate = null;
let variableValues = {};

// DOM Elements
const templateCategory = document.getElementById('templateCategory');
const templateList = document.getElementById('templateList');
const templateDetails = document.getElementById('templateDetails');
const templateName = document.getElementById('templateName');
const templateCategoryBadge = document.getElementById('templateCategoryBadge');
const systemPrompt = document.getElementById('systemPrompt');
const variableInputs = document.getElementById('variableInputs');
const finalPrompt = document.getElementById('finalPrompt');
const customPrompt = document.getElementById('customPrompt');
const customSystemPrompt = document.getElementById('customSystemPrompt');
const temperature = document.getElementById('temperature');
const temperatureValue = document.getElementById('temperatureValue');
const maxTokens = document.getElementById('maxTokens');
const compareBtn = document.getElementById('compareBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const comparisonGrid = document.getElementById('comparisonGrid');

// Initialize
async function init() {
    await loadTemplates();
    setupEventListeners();
}

// Load Templates
async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/templates`);
        templates = await response.json();
        renderTemplateList();
    } catch (error) {
        showError('Failed to load templates: ' + error.message);
    }
}

// Render Template List
function renderTemplateList() {
    const category = templateCategory.value;

    const filteredTemplates = Object.values(templates).filter(t =>
        !category || t.category === category
    );

    templateList.innerHTML = filteredTemplates.map(t => `
        <div class="template-card" data-id="${t.id}">
            <h4>
                ${t.name}
                <span class="category-badge">${t.category}</span>
            </h4>
            <p>${t.description || ''}</p>
            <p style="font-size: 0.8rem; color: var(--text-secondary);">
                Variables: ${t.variables.join(', ')}
            </p>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => selectTemplate(card.dataset.id));
    });
}

// Select Template
function selectTemplate(templateId) {
    selectedTemplate = templates[templateId];
    variableValues = {};

    // Update UI
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.id === templateId);
    });

    templateDetails.classList.remove('hidden');
    templateName.textContent = selectedTemplate.name;
    templateCategoryBadge.textContent = selectedTemplate.category;
    systemPrompt.value = selectedTemplate.system_prompt;

    // Render variable inputs
    variableInputs.innerHTML = selectedTemplate.variables.map(variable => `
        <div class="form-group">
            <label for="var_${variable}">${formatVariableName(variable)}:</label>
            <input
                type="text"
                id="var_${variable}"
                placeholder="Enter ${variable}..."
                value="${selectedTemplate.example_values[variable] || ''}"
            >
        </div>
    `).join('');

    // Add input handlers
    selectedTemplate.variables.forEach(variable => {
        const input = document.getElementById(`var_${variable}`);
        input.addEventListener('input', updateFinalPrompt);
        variableValues[variable] = input.value;
    });

    updateFinalPrompt();
}

// Update Final Prompt
function updateFinalPrompt() {
    if (!selectedTemplate) return;

    let prompt = selectedTemplate.template;
    selectedTemplate.variables.forEach(variable => {
        const input = document.getElementById(`var_${variable}`);
        variableValues[variable] = input.value;
        prompt = prompt.replace(`{{${variable}}}`, input.value || `[${variable}]`);
    });

    finalPrompt.value = prompt;
}

// Format Variable Name
function formatVariableName(name) {
    return name.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Setup Event Listeners
function setupEventListeners() {
    templateCategory.addEventListener('change', renderTemplateList);

    temperature.addEventListener('input', (e) => {
        temperatureValue.textContent = e.target.value;
    });

    compareBtn.addEventListener('click', comparePrompts);

    // Clear custom prompt when template is selected
    customPrompt.addEventListener('input', () => {
        if (customPrompt.value) {
            selectedTemplate = null;
            document.querySelectorAll('.template-card').forEach(card => {
                card.classList.remove('selected');
            });
        }
    });
}

// Compare Prompts
async function comparePrompts() {
    // Get selected providers
    const providerCheckboxes = document.querySelectorAll('input[name="provider"]:checked');
    const providers = Array.from(providerCheckboxes).map(cb => cb.value);

    if (providers.length === 0) {
        showError('Please select at least one provider');
        return;
    }

    // Get prompt
    let prompt, systemPromptText;
    if (customPrompt.value) {
        prompt = customPrompt.value;
        systemPromptText = customSystemPrompt.value || null;
    } else if (selectedTemplate) {
        prompt = finalPrompt.value;
        systemPromptText = selectedTemplate.system_prompt;
    } else {
        showError('Please select a template or enter a custom prompt');
        return;
    }

    // Prepare request
    const request = {
        prompt: prompt,
        system_prompt: systemPromptText,
        providers: providers,
        temperature: parseFloat(temperature.value),
        max_tokens: parseInt(maxTokens.value)
    };

    // Show loading
    showLoading();
    hideError();
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/api/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Comparison failed');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        showError('Comparison failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(data) {
    // Update summary cards
    document.getElementById('fastestProvider').textContent = formatProviderName(data.fastest);
    document.getElementById('cheapestProvider').textContent = formatProviderName(data.cheapest);

    const fastestResult = data.results.find(r => r.provider === data.fastest);
    document.getElementById('fastestTime').textContent = `${fastestResult.latency.toFixed(2)}s`;

    const cheapestResult = data.results.find(r => r.provider === data.cheapest);
    document.getElementById('cheapestCost').textContent = `$${cheapestResult.cost.toFixed(4)}`;

    const totalCost = data.results.reduce((sum, r) => sum + r.cost, 0);
    const totalTokens = data.results.reduce((sum, r) => sum + r.input_tokens + r.output_tokens, 0);
    document.getElementById('totalCost').textContent = `$${totalCost.toFixed(4)}`;
    document.getElementById('totalTokens').textContent = `${totalTokens.toLocaleString()} tokens`;

    // Render comparison grid
    comparisonGrid.innerHTML = data.results.map(result => {
        const isFastest = result.provider === data.fastest;
        const isCheapest = result.provider === data.cheapest;

        return `
            <div class="result-card ${isFastest ? 'fastest' : ''} ${isCheapest ? 'cheapest' : ''}">
                <div class="result-header">
                    <h3>${formatProviderName(result.provider)}</h3>
                    <div class="result-badges">
                        ${isFastest ? '<span class="badge badge-fastest">⚡ Fastest</span>' : ''}
                        ${isCheapest ? '<span class="badge badge-cheapest">💰 Cheapest</span>' : ''}
                    </div>
                </div>

                <div class="result-meta">
                    <div class="meta-item">
                        <span class="meta-label">Latency</span>
                        <span class="meta-value">${result.latency.toFixed(2)}s</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Cost</span>
                        <span class="meta-value">$${result.cost.toFixed(4)}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Tokens</span>
                        <span class="meta-value">${(result.input_tokens + result.output_tokens).toLocaleString()}</span>
                    </div>
                </div>

                <div class="result-content">${escapeHtml(result.response)}</div>
            </div>
        `;
    }).join('');

    resultsSection.classList.remove('hidden');
}

// Format Provider Name
function formatProviderName(provider) {
    const names = {
        'openai': 'GPT-4',
        'anthropic': 'Claude 3.5 Sonnet',
        'openai-gpt35': 'GPT-3.5 Turbo'
    };
    return names[provider] || provider;
}

// Utility Functions
function showLoading() {
    loadingState.classList.remove('hidden');
    compareBtn.disabled = true;
}

function hideLoading() {
    loadingState.classList.add('hidden');
    compareBtn.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    errorState.classList.remove('hidden');
}

function hideError() {
    errorState.classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize app
init();
