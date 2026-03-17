// Main Application Logic

const app = {
    state: {
        programs: [],
        tags: [],
        settings: {},
        runtimes: {},
        viewMode: 'grid',
        search: '',
        sort: 'name',
        filter: 'all',      // 'all', 'favorites', 'running'
        activeTag: null,
        editingProgram: null,
        deletingProgram: null,
    },

    async init() {
        this.bindEvents();
        await this.loadAll();
        this.startPolling();
    },

    bindEvents() {
        // Search
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.state.search = e.target.value;
            this.loadPrograms();
        });

        // Sort
        document.getElementById('sortSelect').addEventListener('change', (e) => {
            this.state.sort = e.target.value;
            this.loadPrograms();
        });

        // View toggle
        document.getElementById('viewToggle').addEventListener('click', () => {
            this.state.viewMode = this.state.viewMode === 'grid' ? 'list' : 'grid';
            document.getElementById('gridIcon').style.display = this.state.viewMode === 'grid' ? 'none' : '';
            document.getElementById('listIcon').style.display = this.state.viewMode === 'list' ? 'none' : '';
            this.renderPrograms();
        });

        // Refresh
        document.getElementById('refreshBtn').addEventListener('click', async () => {
            await API.scan();
            await this.loadPrograms();
            this.showToast('Folder rescanned', 'success');
        });

        // Sidebar filters
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = link.dataset.filter;
                this.state.filter = filter;
                this.state.activeTag = null;
                document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                document.querySelectorAll('.tag-item').forEach(t => t.classList.remove('active'));
                this.loadPrograms();
            });
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
        document.getElementById('closeSettings').addEventListener('click', () => this.closeSettings());
        document.getElementById('settingsOverlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeSettings();
        });
        document.getElementById('saveSettings').addEventListener('click', () => this.saveSettings());

        // Edit modal
        document.getElementById('closeEdit').addEventListener('click', () => this.closeEdit());
        document.getElementById('cancelEdit').addEventListener('click', () => this.closeEdit());
        document.getElementById('saveEdit').addEventListener('click', () => this.saveEdit());
        document.getElementById('editModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeEdit();
        });

        // Delete modal
        document.getElementById('closeDelete').addEventListener('click', () => this.closeDelete());
        document.getElementById('cancelDelete').addEventListener('click', () => this.closeDelete());
        document.getElementById('confirmDelete').addEventListener('click', () => this.confirmDelete());
        document.getElementById('deleteModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeDelete();
        });

        // Add tag
        document.getElementById('addTagBtn').addEventListener('click', () => {
            document.getElementById('addTagModal').classList.add('open');
            document.getElementById('newTagName').value = '';
            document.getElementById('newTagName').focus();
        });
        document.getElementById('closeAddTag').addEventListener('click', () => {
            document.getElementById('addTagModal').classList.remove('open');
        });
        document.getElementById('cancelAddTag').addEventListener('click', () => {
            document.getElementById('addTagModal').classList.remove('open');
        });
        document.getElementById('confirmAddTag').addEventListener('click', () => this.addTag());
        document.getElementById('newTagName').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.addTag();
        });
        document.getElementById('addTagModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) document.getElementById('addTagModal').classList.remove('open');
        });

        // Open folder button (empty state)
        document.getElementById('openFolderBtn').addEventListener('click', async () => {
            const settings = await API.getSettings();
            const folder = settings.watched_folder;
            // Open via a simple endpoint or just show the path
            this.showToast(`Programs folder: ${folder}`, 'success');
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSettings();
                this.closeEdit();
                this.closeDelete();
                document.getElementById('addTagModal').classList.remove('open');
            }
            // Ctrl+F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
        });
    },

    async loadAll() {
        await Promise.all([
            this.loadPrograms(),
            this.loadTags(),
        ]);
    },

    async loadPrograms() {
        const params = {
            search: this.state.search || undefined,
            sort: this.state.sort,
            tag: this.state.activeTag || undefined,
            favorites: this.state.filter === 'favorites' || undefined,
        };

        try {
            let programs = await API.getPrograms(params);

            if (this.state.filter === 'running') {
                programs = programs.filter(p => p.running);
            }

            this.state.programs = programs;
            this.renderPrograms();
            this.updateCounts();
        } catch (err) {
            this.showToast('Failed to load programs', 'error');
        }
    },

    async loadTags() {
        try {
            this.state.tags = await API.getTags();
            this.renderTags();
        } catch (err) {
            console.error('Failed to load tags:', err);
        }
    },

    renderPrograms() {
        const grid = document.getElementById('programGrid');
        const empty = document.getElementById('emptyState');
        const programs = this.state.programs;

        if (programs.length === 0) {
            grid.style.display = 'none';
            empty.style.display = 'flex';
            return;
        }

        grid.style.display = '';
        empty.style.display = 'none';

        if (this.state.viewMode === 'list') {
            grid.classList.add('list-view');
        } else {
            grid.classList.remove('list-view');
        }

        grid.innerHTML = programs.map(p => renderProgramCard(p, this.state.viewMode)).join('');
    },

    renderTags() {
        document.getElementById('tagList').innerHTML = renderTagList(this.state.tags, this.state.activeTag);
    },

    updateCounts() {
        const all = this.state.programs;
        document.getElementById('countAll').textContent = all.length;

        // We need to make separate calls for accurate counts
        // For now, count from current loaded data
        API.getPrograms({ favorites: true }).then(favs => {
            document.getElementById('countFavorites').textContent = favs.length;
        });

        const running = all.filter(p => p.running).length;
        document.getElementById('countRunning').textContent = running;
    },

    // --- Actions ---

    async launchProgram(id, event) {
        event.stopPropagation();
        try {
            await API.launchProgram(id);
            this.showToast('Program launched!', 'success');
            setTimeout(() => this.loadPrograms(), 500);
        } catch (err) {
            this.showToast(`Launch failed: ${err.message}`, 'error');
        }
    },

    async stopProgram(id, event) {
        event.stopPropagation();
        try {
            await API.stopProgram(id);
            this.showToast('Program stopped', 'success');
            await this.loadPrograms();
        } catch (err) {
            this.showToast(`Stop failed: ${err.message}`, 'error');
        }
    },

    async toggleFavorite(id, event) {
        event.stopPropagation();
        const prog = this.state.programs.find(p => p.id === id);
        if (!prog) return;
        try {
            await API.updateProgram(id, { favorite: !prog.favorite });
            await this.loadPrograms();
        } catch (err) {
            this.showToast('Failed to update favorite', 'error');
        }
    },

    async openFolder(id, event) {
        event.stopPropagation();
        const prog = this.state.programs.find(p => p.id === id);
        if (!prog) return;
        this.showToast(`Path: ${prog.path}`, 'success');
    },

    filterByTag(tagName) {
        if (this.state.activeTag === tagName) {
            this.state.activeTag = null;
        } else {
            this.state.activeTag = tagName;
        }
        this.state.filter = 'all';
        document.querySelectorAll('.sidebar-link').forEach(l => {
            l.classList.toggle('active', l.dataset.filter === 'all');
        });
        this.renderTags();
        this.loadPrograms();
    },

    // --- Edit ---

    async editProgram(id) {
        try {
            const prog = await API.getProgram(id);
            this.state.editingProgram = prog;

            document.getElementById('editName').value = prog.name;
            document.getElementById('editDescription').value = prog.description || '';
            document.getElementById('editEntryPoint').value = prog.entry_point || '';

            // Tags checkboxes
            const editTags = document.getElementById('editTags');
            const progTagIds = new Set((prog.tags || []).map(t => t.id));
            editTags.innerHTML = this.state.tags.map(tag => {
                const selected = progTagIds.has(tag.id) ? 'selected' : '';
                return `<div class="edit-tag-checkbox ${selected}" data-tag-id="${tag.id}" onclick="this.classList.toggle('selected')">
                    ${escapeHtml(tag.name)}
                </div>`;
            }).join('') || '<span style="color: var(--text-muted); font-size: 13px;">No tags created yet</span>';

            // Info
            document.getElementById('editInfo').innerHTML = `
                <span class="info-label">Type:</span><span class="info-value">${TYPE_LABELS[prog.program_type] || 'Unknown'}</span>
                <span class="info-label">Path:</span><span class="info-value" style="word-break:break-all">${escapeHtml(prog.path)}</span>
                <span class="info-label">Launches:</span><span class="info-value">${prog.launch_count || 0}</span>
                <span class="info-label">Last launch:</span><span class="info-value">${formatDate(prog.last_launched)}</span>
                <span class="info-label">Added:</span><span class="info-value">${formatDate(prog.date_added)}</span>
            `;

            document.getElementById('editModal').classList.add('open');
        } catch (err) {
            this.showToast('Failed to load program details', 'error');
        }
    },

    async saveEdit() {
        const prog = this.state.editingProgram;
        if (!prog) return;

        const selectedTags = Array.from(document.querySelectorAll('#editTags .edit-tag-checkbox.selected'))
            .map(el => parseInt(el.dataset.tagId));

        try {
            await API.updateProgram(prog.id, {
                name: document.getElementById('editName').value,
                description: document.getElementById('editDescription').value,
                entry_point: document.getElementById('editEntryPoint').value,
                tag_ids: selectedTags,
            });
            this.closeEdit();
            await this.loadPrograms();
            this.showToast('Program updated', 'success');
        } catch (err) {
            this.showToast('Failed to save changes', 'error');
        }
    },

    closeEdit() {
        document.getElementById('editModal').classList.remove('open');
        this.state.editingProgram = null;
    },

    // --- Delete ---

    deleteProgram(id, event) {
        event.stopPropagation();
        const prog = this.state.programs.find(p => p.id === id);
        if (!prog) return;
        this.state.deletingProgram = prog;
        document.getElementById('deleteName').textContent = prog.name;
        document.getElementById('deleteModal').classList.add('open');
    },

    async confirmDelete() {
        const prog = this.state.deletingProgram;
        if (!prog) return;
        try {
            await API.deleteProgram(prog.id);
            this.closeDelete();
            await this.loadPrograms();
            this.showToast('Program removed', 'success');
        } catch (err) {
            this.showToast('Failed to delete program', 'error');
        }
    },

    closeDelete() {
        document.getElementById('deleteModal').classList.remove('open');
        this.state.deletingProgram = null;
    },

    // --- Tags ---

    async addTag() {
        const name = document.getElementById('newTagName').value.trim();
        if (!name) return;
        try {
            await API.createTag(name);
            document.getElementById('addTagModal').classList.remove('open');
            await this.loadTags();
            this.showToast(`Tag "${name}" created`, 'success');
        } catch (err) {
            this.showToast('Failed to create tag', 'error');
        }
    },

    async deleteTag(id, event) {
        event.stopPropagation();
        try {
            await API.deleteTag(id);
            if (this.state.activeTag) {
                const tag = this.state.tags.find(t => t.id === id);
                if (tag && tag.name === this.state.activeTag) {
                    this.state.activeTag = null;
                }
            }
            await this.loadTags();
            await this.loadPrograms();
            this.showToast('Tag deleted', 'success');
        } catch (err) {
            this.showToast('Failed to delete tag', 'error');
        }
    },

    // --- Settings ---

    async openSettings() {
        try {
            const [settings, runtimes] = await Promise.all([
                API.getSettings(),
                API.getRuntimes(),
            ]);
            this.state.settings = settings;
            this.state.runtimes = runtimes;

            document.getElementById('settingWatchedFolder').value = settings.watched_folder || '';
            document.getElementById('settingPython').value = settings.runtime_python === 'auto' ? '' : (settings.runtime_python || '');
            document.getElementById('settingNode').value = settings.runtime_node === 'auto' ? '' : (settings.runtime_node || '');

            document.getElementById('pythonDetected').textContent = `Detected: ${runtimes.python || 'not found'}`;
            document.getElementById('nodeDetected').textContent = `Detected: ${runtimes.node || 'not found'}`;

            document.getElementById('settingsOverlay').classList.add('open');
        } catch (err) {
            this.showToast('Failed to load settings', 'error');
        }
    },

    closeSettings() {
        document.getElementById('settingsOverlay').classList.remove('open');
    },

    async saveSettings() {
        const data = {
            watched_folder: document.getElementById('settingWatchedFolder').value,
            runtime_python: document.getElementById('settingPython').value || 'auto',
            runtime_node: document.getElementById('settingNode').value || 'auto',
        };
        try {
            await API.updateSettings(data);
            this.closeSettings();
            await this.loadPrograms();
            this.showToast('Settings saved', 'success');
        } catch (err) {
            this.showToast('Failed to save settings', 'error');
        }
    },

    // --- Polling ---

    startPolling() {
        setInterval(() => this.loadPrograms(), 5000);
    },

    // --- Toast ---

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast toast-${type} show`;
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    },
};

// Boot
document.addEventListener('DOMContentLoaded', () => app.init());
