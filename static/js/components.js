// UI Component Rendering

const TYPE_LABELS = {
    python: 'Python',
    node: 'Node.js',
    html: 'Web App',
    exe: 'Executable',
    batch: 'Batch Script',
    powershell: 'PowerShell',
    npm: 'NPM Project',
    unknown: 'Unknown',
};

const TYPE_ICONS = {
    python: 'PY',
    node: 'JS',
    html: '< >',
    exe: 'EXE',
    batch: 'BAT',
    powershell: 'PS',
    npm: 'NPM',
    unknown: '?',
};

function formatDate(dateStr) {
    if (!dateStr) return 'Never';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString();
}

function renderProgramCard(program, viewMode) {
    const tags = (program.tags || [])
        .map(t => `<span class="tag-badge">${escapeHtml(t.name)}</span>`)
        .join('');

    const typeClass = `type-${program.program_type || 'unknown'}`;
    const typeIcon = TYPE_ICONS[program.program_type] || '?';
    const typeLabel = TYPE_LABELS[program.program_type] || 'Unknown';
    const runningDot = program.running ? '<div class="running-indicator" title="Running"></div>' : '';
    const favClass = program.favorite ? 'favorited' : '';
    const favIcon = program.favorite
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>';

    const launchBtn = program.running
        ? `<button class="btn btn-stop" onclick="app.stopProgram(${program.id}, event)">Stop</button>`
        : `<button class="btn btn-launch" onclick="app.launchProgram(${program.id}, event)">Launch</button>`;

    return `
        <div class="program-card" onclick="app.editProgram(${program.id})" data-id="${program.id}">
            <div class="program-card-header">
                <div class="program-type-icon ${typeClass}">${typeIcon}</div>
                <div class="program-card-title">
                    <h3>${escapeHtml(program.name)}</h3>
                    <div class="program-type-label">${typeLabel}</div>
                </div>
                ${runningDot}
            </div>
            <div class="program-card-desc">${escapeHtml(program.description || 'No description')}</div>
            ${tags ? `<div class="program-card-tags">${tags}</div>` : ''}
            <div class="program-card-meta">
                <span>Launched ${program.launch_count || 0}x</span>
                <span>${formatDate(program.last_launched)}</span>
            </div>
            <div class="program-card-actions">
                ${launchBtn}
                <button class="btn btn-icon ${favClass}" onclick="app.toggleFavorite(${program.id}, event)" title="Favorite">
                    ${favIcon}
                </button>
                <button class="btn btn-icon" onclick="app.openFolder(${program.id}, event)" title="Open folder">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                </button>
                <button class="btn btn-icon" onclick="app.deleteProgram(${program.id}, event)" title="Delete">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
}

function renderTagList(tags, activeTag) {
    if (!tags.length) {
        return '<div class="tag-item" style="color: var(--text-muted); font-size: 12px; padding-left: 12px;">No tags yet</div>';
    }
    return tags.map(tag => {
        const active = activeTag === tag.name ? 'active' : '';
        return `
            <div class="tag-item ${active}" onclick="app.filterByTag('${escapeHtml(tag.name)}')">
                <span class="tag-dot"></span>
                ${escapeHtml(tag.name)}
                <button class="tag-delete" onclick="app.deleteTag(${tag.id}, event)" title="Delete tag">&times;</button>
            </div>
        `;
    }).join('');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}
