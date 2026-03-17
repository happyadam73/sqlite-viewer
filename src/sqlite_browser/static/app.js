(() => {
  const root = document.documentElement;
  const themeToggle = document.querySelector('[data-testid="theme-toggle"]');
  const currentDbLabel = document.querySelector('[data-testid="current-db-label"]');
  const loadingIndicator = document.querySelector('[data-testid="loading-indicator"]');
  const errorBanner = document.querySelector('[data-testid="error-banner"]');
  const tableList = document.querySelector('[data-testid="table-list"]');
  const explorerHint = document.querySelector('[data-role="explorer-hint"]');
  const selectedTableTitle = document.querySelector('[data-testid="selected-table-title"]');
  const selectedTableMeta = document.querySelector('[data-role="selected-table-meta"]');
  const emptyState = document.querySelector('[data-testid="empty-state"]');
  const emptyStateEyebrow = document.querySelector('[data-role="empty-state-eyebrow"]');
  const emptyStateTitle = document.querySelector('[data-role="empty-state-title"]');
  const emptyStateCopy = document.querySelector('[data-role="empty-state-copy"]');
  const emptyStateAction = document.querySelector('[data-role="empty-state-action"]');
  const dataGrid = document.querySelector('[data-testid="data-grid"]');
  const dataGridHeader = document.querySelector('[data-testid="data-grid-header"]');
  const dataGridBody = document.querySelector('[data-testid="data-grid-body"]');
  const fileInput = document.getElementById("db-file-input");
  const openFileButtons = document.querySelectorAll('[data-action="open-file"]');
  const storageKey = "sqlite-browser-theme";
  const state = {
    expandedTables: new Set(),
    loadingCount: 0,
    rowRequestToken: 0,
    schemaCache: new Map(),
    selectedTableName: null,
    sourceMode: null,
    tableNames: [],
  };

  function applyTheme(choice) {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const resolvedTheme = choice === "system" ? (prefersDark ? "dark" : "light") : choice;
    root.dataset.theme = resolvedTheme;
    if (themeToggle instanceof HTMLButtonElement) {
      themeToggle.dataset.themeChoice = choice;
      themeToggle.setAttribute("aria-pressed", resolvedTheme === "dark" ? "true" : "false");
      themeToggle.textContent = resolvedTheme === "dark" ? "Switch to light theme" : "Switch to dark theme";
    }
  }

  function beginLoading(message) {
    state.loadingCount += 1;
    if (loadingIndicator instanceof HTMLElement) {
      loadingIndicator.hidden = false;
      loadingIndicator.textContent = message;
    }
  }

  function endLoading() {
    state.loadingCount = Math.max(0, state.loadingCount - 1);
    if (state.loadingCount === 0 && loadingIndicator instanceof HTMLElement) {
      loadingIndicator.hidden = true;
      loadingIndicator.textContent = "Loading";
    }
  }

  function clearBanner() {
    if (!(errorBanner instanceof HTMLElement)) {
      return;
    }

    errorBanner.hidden = true;
    errorBanner.textContent = "";
  }

  function showBanner(message) {
    if (!(errorBanner instanceof HTMLElement)) {
      return;
    }

    errorBanner.hidden = false;
    errorBanner.textContent = message;
  }

  async function requestJson(url) {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
    });
    const isJson = response.headers.get("content-type")?.includes("application/json");
    const payload = isJson ? await response.json() : null;

    if (!response.ok) {
      const message = payload?.error?.message ?? `The request to ${url} failed with status ${response.status}.`;
      throw new Error(message);
    }

    return payload;
  }

  async function loadStatus() {
    beginLoading("Loading database status...");
    try {
      return await requestJson("/api/status");
    } finally {
      endLoading();
    }
  }

  async function loadTables() {
    beginLoading("Loading table explorer...");
    try {
      return await requestJson("/api/tables");
    } finally {
      endLoading();
    }
  }

  async function loadSchema(tableName) {
    beginLoading(`Loading schema for ${tableName}...`);
    try {
      return await requestJson(`/api/tables/${encodeURIComponent(tableName)}/schema`);
    } finally {
      endLoading();
    }
  }

  async function loadRows(tableName) {
    beginLoading(`Loading preview rows for ${tableName}...`);
    try {
      return await requestJson(`/api/tables/${encodeURIComponent(tableName)}/rows`);
    } finally {
      endLoading();
    }
  }

  async function uploadDatabase(file) {
    beginLoading(`Opening ${file.name}...`);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/open-upload", {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      });
      const isJson = response.headers.get("content-type")?.includes("application/json");
      const payload = isJson ? await response.json() : null;

      if (!response.ok) {
        const message = payload?.error?.message ?? "The selected file could not be opened.";
        throw new Error(message);
      }

      return payload;
    } finally {
      endLoading();
    }
  }

  function setExplorerHint(message) {
    if (explorerHint instanceof HTMLElement) {
      explorerHint.textContent = message;
    }
  }

  function setCurrentDbLabel(label) {
    if (currentDbLabel instanceof HTMLElement) {
      currentDbLabel.textContent = label;
    }
  }

  function setSelectedTableMeta(message) {
    if (selectedTableMeta instanceof HTMLElement) {
      selectedTableMeta.textContent = message;
      selectedTableMeta.hidden = message.length === 0;
    }
  }

  function showEmptyState({ eyebrow, title, copy, showAction }) {
    if (emptyState instanceof HTMLElement) {
      emptyState.hidden = false;
    }
    if (emptyStateEyebrow instanceof HTMLElement) {
      emptyStateEyebrow.textContent = eyebrow;
    }
    if (emptyStateTitle instanceof HTMLElement) {
      emptyStateTitle.textContent = title;
    }
    if (emptyStateCopy instanceof HTMLElement) {
      emptyStateCopy.textContent = copy;
    }
    if (emptyStateAction instanceof HTMLElement) {
      emptyStateAction.hidden = !showAction;
    }
  }

  function hideEmptyState() {
    if (emptyState instanceof HTMLElement) {
      emptyState.hidden = true;
    }
  }

  function resetPreviewState() {
    state.rowRequestToken += 1;
    state.selectedTableName = null;
    updateSelectedTableStyles();

    if (selectedTableTitle instanceof HTMLElement) {
      selectedTableTitle.textContent = "No table selected";
    }

    setSelectedTableMeta("");
    renderGridPlaceholder("Column headers will appear here.", "Row previews will appear here after a table is selected.");
  }

  function resetDatabaseState() {
    state.expandedTables.clear();
    state.schemaCache.clear();
    state.tableNames = [];
    resetPreviewState();
  }

  function createGridCell(text, className = "") {
    const cell = document.createElement("div");
    cell.className = className ? `grid-cell ${className}` : "grid-cell";
    cell.textContent = text;
    cell.title = text;
    return cell;
  }

  function renderGridPlaceholder(headerText, bodyText) {
    if (!(dataGridHeader instanceof HTMLElement) || !(dataGridBody instanceof HTMLElement)) {
      return;
    }

    const headerRow = document.createElement("div");
    headerRow.className = "grid-row";
    headerRow.appendChild(createGridCell(headerText, "grid-cell--placeholder"));

    const bodyRow = document.createElement("div");
    bodyRow.className = "grid-row";
    bodyRow.appendChild(createGridCell(bodyText, "grid-cell--placeholder"));

    dataGridHeader.replaceChildren(headerRow);
    dataGridBody.replaceChildren(bodyRow);
    if (dataGrid instanceof HTMLElement) {
      dataGrid.scrollLeft = 0;
      dataGrid.scrollTop = 0;
    }
  }

  function createSchemaBadge(text) {
    const badge = document.createElement("span");
    badge.className = "schema-badge";
    badge.textContent = text;
    return badge;
  }

  function renderSchemaList(schemaList, columns) {
    const items = columns.map((column) => {
      const item = document.createElement("li");
      item.className = "schema-item";

      const summary = document.createElement("div");
      summary.className = "schema-item__summary";

      const name = document.createElement("span");
      name.className = "schema-item__name";
      name.textContent = column.name;

      const type = document.createElement("span");
      type.className = "schema-item__type";
      type.textContent = column.type || "untyped";

      summary.append(name, type);

      const badges = document.createElement("div");
      badges.className = "schema-item__badges";
      if (column.is_primary_key) {
        badges.appendChild(createSchemaBadge("PK"));
      }
      if (column.not_null) {
        badges.appendChild(createSchemaBadge("NOT NULL"));
      }
      if (column.default_value !== null) {
        badges.appendChild(createSchemaBadge(`DEFAULT ${String(column.default_value)}`));
      }

      item.append(summary, badges);
      return item;
    });

    schemaList.replaceChildren(...items);
  }

  function updateSelectedTableStyles() {
    tableList?.querySelectorAll(".table-select").forEach((element) => {
      if (!(element instanceof HTMLElement)) {
        return;
      }
      element.classList.toggle("is-selected", element.dataset.tableName === state.selectedTableName);
    });
  }

  async function toggleSchema(tableName, expandButton, schemaList) {
    const isExpanded = state.expandedTables.has(tableName);
    if (isExpanded) {
      state.expandedTables.delete(tableName);
      expandButton.setAttribute("aria-expanded", "false");
      expandButton.textContent = "+";
      schemaList.hidden = true;
      return;
    }

    if (!state.schemaCache.has(tableName)) {
      clearBanner();
      expandButton.disabled = true;
      try {
        const payload = await loadSchema(tableName);
        state.schemaCache.set(tableName, payload.columns ?? []);
      } catch (error) {
        showBanner(error instanceof Error ? error.message : "The schema could not be loaded.");
        return;
      } finally {
        expandButton.disabled = false;
      }
    }

    renderSchemaList(schemaList, state.schemaCache.get(tableName) ?? []);
    state.expandedTables.add(tableName);
    expandButton.setAttribute("aria-expanded", "true");
    expandButton.textContent = "-";
    schemaList.hidden = false;
  }

  function renderRows(tableName, payload) {
    if (
      !(selectedTableTitle instanceof HTMLElement) ||
      !(dataGridHeader instanceof HTMLElement) ||
      !(dataGridBody instanceof HTMLElement)
    ) {
      return;
    }

    const headerRow = document.createElement("div");
    headerRow.className = "grid-row";
    payload.columns.forEach((columnName) => {
      headerRow.appendChild(createGridCell(columnName, "grid-cell--header"));
    });

    const bodyRows = payload.rows.length
      ? payload.rows.map((row) => {
          const rowElement = document.createElement("div");
          rowElement.className = "grid-row";

          row.forEach((value) => {
            const text = value === null ? "NULL" : String(value);
            const cell = createGridCell(text, value === null ? "grid-cell--null" : "");
            rowElement.appendChild(cell);
          });

          return rowElement;
        })
      : (() => {
          const emptyRow = document.createElement("div");
          emptyRow.className = "grid-row";
          emptyRow.appendChild(createGridCell("No preview rows found for this table.", "grid-cell--placeholder"));
          return [emptyRow];
        })();

    selectedTableTitle.textContent = tableName;
    setSelectedTableMeta(`Showing ${payload.rows.length} row(s) from the first ${payload.limit} preview results.`);
    hideEmptyState();
    dataGridHeader.replaceChildren(headerRow);
    dataGridBody.replaceChildren(...bodyRows);
    if (dataGrid instanceof HTMLElement) {
      dataGrid.scrollLeft = 0;
      dataGrid.scrollTop = 0;
    }
  }

  async function selectTable(tableName) {
    clearBanner();
    state.selectedTableName = tableName;
    state.rowRequestToken += 1;
    const requestToken = state.rowRequestToken;
    updateSelectedTableStyles();

    if (selectedTableTitle instanceof HTMLElement) {
      selectedTableTitle.textContent = tableName;
    }
    setSelectedTableMeta("Loading preview rows...");
    hideEmptyState();
    renderGridPlaceholder("Loading columns...", "Loading preview rows...");

    try {
      const payload = await loadRows(tableName);
      if (requestToken !== state.rowRequestToken) {
        return;
      }
      renderRows(tableName, payload);
    } catch (error) {
      if (requestToken !== state.rowRequestToken) {
        return;
      }
      setSelectedTableMeta("");
      showBanner(error instanceof Error ? error.message : "The preview rows could not be loaded.");
      renderGridPlaceholder("Preview unavailable", "Try another table or reload the page.");
      showEmptyState({
        eyebrow: "Preview Unavailable",
        title: `Couldn't load ${tableName}`,
        copy: "The app is still running. Try a different table or reload the page to request the preview again.",
        showAction: false,
      });
    }
  }

  function renderTableList(tables) {
    if (!(tableList instanceof HTMLElement)) {
      return;
    }

    state.tableNames = tables.map((table) => table.name);
    const items = tables.map((table) => {
      const listItem = document.createElement("li");
      listItem.className = "table-item";
      listItem.dataset.tableName = table.name;
      listItem.setAttribute("data-testid", `table-item-${table.name}`);

      const row = document.createElement("div");
      row.className = "table-item__row";

      const expandButton = document.createElement("button");
      expandButton.className = "table-expand";
      expandButton.type = "button";
      expandButton.textContent = "+";
      expandButton.dataset.tableName = table.name;
      expandButton.setAttribute("data-testid", `table-expand-${table.name}`);
      expandButton.setAttribute("aria-expanded", "false");
      expandButton.setAttribute("aria-label", `Show schema for ${table.name}`);

      const selectButton = document.createElement("button");
      selectButton.className = "table-select";
      selectButton.type = "button";
      selectButton.dataset.tableName = table.name;
      selectButton.textContent = table.name;

      const schemaList = document.createElement("ul");
      schemaList.className = "schema-list";
      schemaList.dataset.tableName = table.name;
      schemaList.setAttribute("data-testid", `schema-list-${table.name}`);
      schemaList.hidden = true;

      expandButton.addEventListener("click", async () => {
        await toggleSchema(table.name, expandButton, schemaList);
      });

      selectButton.addEventListener("click", async () => {
        await selectTable(table.name);
      });

      row.append(expandButton, selectButton);
      listItem.append(row, schemaList);
      return listItem;
    });

    tableList.replaceChildren(...items);
    updateSelectedTableStyles();
  }

  async function renderLoadedDatabase({ dbLabel, sourceMode, tables }) {
    state.sourceMode = sourceMode ?? null;
    setCurrentDbLabel(dbLabel);
    renderTableList(tables);

    if (tables.length === 0) {
      setExplorerHint("This database is loaded, but it does not expose any user tables.");
      showEmptyState({
        eyebrow: "Database Ready",
        title: "No tables available",
        copy: "This database loaded successfully, but there are no user tables available to preview.",
        showAction: false,
      });
      setSelectedTableMeta("");
      return;
    }

    setExplorerHint("Expand a table to inspect its schema, or select one to preview rows.");
    await selectTable(tables[0].name);
  }

  async function initializeBrowser() {
    clearBanner();
    resetDatabaseState();

    try {
      const status = await loadStatus();
      state.sourceMode = status.source_mode ?? null;
      setCurrentDbLabel(status.db_label ?? "No database loaded");

      if (!status.db_loaded) {
        renderTableList([]);
        setExplorerHint("Load a SQLite database to explore tables and schema details.");
        showEmptyState({
          eyebrow: "Start Here",
          title: "No database loaded yet",
          copy: "Launch the app with a SQLite path, or choose a local SQLite file to browse without restarting the app.",
          showAction: true,
        });
        setSelectedTableMeta("");
        return;
      }

      const tablesPayload = await loadTables();
      await renderLoadedDatabase({
        dbLabel: status.db_label ?? "No database loaded",
        sourceMode: status.source_mode ?? null,
        tables: tablesPayload.tables ?? [],
      });
    } catch (error) {
      renderTableList([]);
      setExplorerHint("The explorer could not be loaded.");
      setSelectedTableMeta("");
      showBanner(error instanceof Error ? error.message : "The application could not finish loading.");
      showEmptyState({
        eyebrow: "Backend Error",
        title: "The browser could not load this session",
        copy: "Check the error banner above, then reload the page or restart the app if the problem persists.",
        showAction: false,
      });
    }
  }

  const savedTheme = window.localStorage.getItem(storageKey) ?? "system";
  applyTheme(savedTheme);

  themeToggle?.addEventListener("click", () => {
    const currentChoice = themeToggle.dataset.themeChoice ?? "system";
    const nextChoice = currentChoice === "dark" ? "light" : "dark";
    window.localStorage.setItem(storageKey, nextChoice);
    applyTheme(nextChoice);
  });

  openFileButtons.forEach((button) => {
    button.addEventListener("click", () => {
      fileInput?.click();
    });
  });

  fileInput?.addEventListener("change", async () => {
    const file = fileInput?.files?.[0];
    if (fileInput instanceof HTMLInputElement) {
      fileInput.value = "";
    }

    if (!(file instanceof File)) {
      return;
    }

    clearBanner();

    try {
      const payload = await uploadDatabase(file);
      resetDatabaseState();
      await renderLoadedDatabase({
        dbLabel: payload.db_label,
        sourceMode: payload.source_mode,
        tables: payload.tables ?? [],
      });
    } catch (error) {
      showBanner(error instanceof Error ? error.message : "The selected file could not be opened.");
    }
  });

  void initializeBrowser();
})();
