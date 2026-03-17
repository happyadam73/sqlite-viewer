(() => {
  const DEFAULT_PAGE_SIZE = 100;
  const MIN_EXPLORER_WIDTH = 288;
  const MIN_DATA_WIDTH = 360;
  const SPLITTER_KEYBOARD_STEP = 24;
  const root = document.documentElement;
  const workspace = document.querySelector('[data-role="workspace"]');
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
  const paneSplitter = document.querySelector('[data-testid="pane-splitter"]');
  const paginationControls = document.querySelector('[data-testid="pagination-controls"]');
  const paginationPageLabel = document.querySelector('[data-testid="pagination-page-label"]');
  const paginationPageSize = document.querySelector('[data-testid="pagination-page-size"]');
  const paginationPrevButton = document.querySelector('[data-testid="pagination-prev-button"]');
  const paginationNextButton = document.querySelector('[data-testid="pagination-next-button"]');
  const fileInput = document.getElementById("db-file-input");
  const openFileButtons = document.querySelectorAll('[data-action="open-file"]');
  const themeStorageKey = "sqlite-browser-theme";
  const themeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const state = {
    activePointerId: null,
    expandedTables: new Set(),
    loadingCount: 0,
    previewPage: 1,
    previewPageSize: DEFAULT_PAGE_SIZE,
    rowRequestToken: 0,
    schemaCache: new Map(),
    selectedTableName: null,
    sourceMode: null,
    tableNames: [],
    totalPages: 1,
    totalRows: 0,
  };

  function getResolvedTheme(choice) {
    if (choice === "system") {
      return themeMediaQuery.matches ? "dark" : "light";
    }

    return choice;
  }

  function applyTheme(choice) {
    const resolvedTheme = getResolvedTheme(choice);
    root.dataset.theme = resolvedTheme;
    root.dataset.themeChoice = choice;

    if (themeToggle instanceof HTMLButtonElement) {
      themeToggle.dataset.themeChoice = choice;
      themeToggle.setAttribute("aria-checked", resolvedTheme === "dark" ? "true" : "false");
      themeToggle.setAttribute("aria-pressed", resolvedTheme === "dark" ? "true" : "false");
      themeToggle.title =
        choice === "system"
          ? `Following system theme: ${resolvedTheme}`
          : `Theme locked to ${resolvedTheme}`;
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

  async function loadRows(tableName, { page = 1, pageSize = state.previewPageSize } = {}) {
    beginLoading(`Loading preview rows for ${tableName}...`);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      return await requestJson(`/api/tables/${encodeURIComponent(tableName)}/rows?${params.toString()}`);
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

  function setPageSizeControl(pageSize) {
    if (paginationPageSize instanceof HTMLSelectElement) {
      paginationPageSize.value = String(pageSize);
    }
  }

  function hidePaginationControls() {
    state.previewPage = 1;
    state.totalPages = 1;
    state.totalRows = 0;
    setPageSizeControl(state.previewPageSize);

    if (paginationControls instanceof HTMLElement) {
      paginationControls.hidden = true;
    }
    if (paginationPageLabel instanceof HTMLElement) {
      paginationPageLabel.textContent = "Page 1 of 1";
    }
    if (paginationPrevButton instanceof HTMLButtonElement) {
      paginationPrevButton.disabled = true;
    }
    if (paginationNextButton instanceof HTMLButtonElement) {
      paginationNextButton.disabled = true;
    }
  }

  function updatePaginationControls(payload) {
    state.previewPage = payload.page;
    state.previewPageSize = payload.page_size;
    state.totalRows = payload.total_rows;
    state.totalPages = payload.total_pages;
    setPageSizeControl(payload.page_size);

    if (paginationPageLabel instanceof HTMLElement) {
      paginationPageLabel.textContent = `Page ${payload.page} of ${payload.total_pages}`;
    }
    if (paginationPrevButton instanceof HTMLButtonElement) {
      paginationPrevButton.disabled = !payload.has_previous;
    }
    if (paginationNextButton instanceof HTMLButtonElement) {
      paginationNextButton.disabled = !payload.has_next;
    }
    if (paginationControls instanceof HTMLElement) {
      paginationControls.hidden = payload.total_rows <= payload.page_size;
    }
  }

  function resetGridScroll({ resetHorizontal = true, resetVertical = true } = {}) {
    if (!(dataGrid instanceof HTMLElement)) {
      return;
    }

    if (resetHorizontal) {
      dataGrid.scrollLeft = 0;
    }
    if (resetVertical) {
      dataGrid.scrollTop = 0;
    }
  }

  function resetPreviewState() {
    state.rowRequestToken += 1;
    state.selectedTableName = null;
    state.previewPage = 1;
    state.previewPageSize = DEFAULT_PAGE_SIZE;
    updateSelectedTableStyles();

    if (selectedTableTitle instanceof HTMLElement) {
      selectedTableTitle.textContent = "No table selected";
    }

    setSelectedTableMeta("");
    hidePaginationControls();
    renderGridPlaceholder("Column headers will appear here.", "Row previews will appear here after a table is selected.");
  }

  function resetDatabaseState() {
    state.expandedTables.clear();
    state.schemaCache.clear();
    state.tableNames = [];
    resetPreviewState();
  }

  function createGridCell(text, classes = []) {
    const cell = document.createElement("div");
    const classNames = ["grid-cell", ...classes].filter(Boolean);
    cell.className = classNames.join(" ");
    cell.textContent = text;
    cell.title = text;
    return cell;
  }

  function setGridColumnCount(columnCount) {
    if (!(dataGrid instanceof HTMLElement)) {
      return;
    }

    dataGrid.style.setProperty("--grid-column-count", String(Math.max(1, columnCount)));
  }

  function renderGridPlaceholder(headerText, bodyText) {
    if (!(dataGridHeader instanceof HTMLElement) || !(dataGridBody instanceof HTMLElement)) {
      return;
    }

    setGridColumnCount(1);

    const headerRow = document.createElement("div");
    headerRow.className = "grid-row grid-row--header";
    headerRow.appendChild(createGridCell(headerText, ["grid-cell--placeholder", "grid-cell--first-column"]));

    const bodyRow = document.createElement("div");
    bodyRow.className = "grid-row";
    bodyRow.appendChild(createGridCell(bodyText, ["grid-cell--placeholder", "grid-cell--first-column"]));

    dataGridHeader.replaceChildren(headerRow);
    dataGridBody.replaceChildren(bodyRow);
    resetGridScroll();
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
    schemaList.hidden = false;
  }

  function buildRowsSummary(payload) {
    if (payload.total_rows === 0) {
      return "No rows found in this table.";
    }

    const startRow = (payload.page - 1) * payload.page_size + 1;
    const endRow = startRow + payload.rows.length - 1;
    return `Showing rows ${startRow}-${endRow} of ${payload.total_rows}. Page ${payload.page} of ${payload.total_pages}.`;
  }

  function renderRows(tableName, payload, { resetHorizontalScroll = true } = {}) {
    if (
      !(selectedTableTitle instanceof HTMLElement) ||
      !(dataGridHeader instanceof HTMLElement) ||
      !(dataGridBody instanceof HTMLElement)
    ) {
      return;
    }

    setGridColumnCount(payload.columns.length);

    const headerRow = document.createElement("div");
    headerRow.className = "grid-row grid-row--header";
    payload.columns.forEach((columnName, columnIndex) => {
      const classes = ["grid-cell--header"];
      if (columnIndex === 0) {
        classes.push("grid-cell--first-column");
      }
      headerRow.appendChild(createGridCell(columnName, classes));
    });

    const bodyRows = payload.rows.length
      ? payload.rows.map((row) => {
          const rowElement = document.createElement("div");
          rowElement.className = "grid-row";

          row.forEach((value, columnIndex) => {
            const classes = [];
            if (value === null) {
              classes.push("grid-cell--null");
            }
            if (columnIndex === 0) {
              classes.push("grid-cell--first-column");
            }
            rowElement.appendChild(createGridCell(value === null ? "NULL" : String(value), classes));
          });

          return rowElement;
        })
      : (() => {
          const emptyRow = document.createElement("div");
          emptyRow.className = "grid-row";
          emptyRow.appendChild(
            createGridCell("No preview rows found for this table.", [
              "grid-cell--placeholder",
              "grid-cell--first-column",
            ])
          );
          return [emptyRow];
        })();

    selectedTableTitle.textContent = tableName;
    setSelectedTableMeta(buildRowsSummary(payload));
    hideEmptyState();
    updatePaginationControls(payload);
    dataGridHeader.replaceChildren(headerRow);
    dataGridBody.replaceChildren(...bodyRows);
    resetGridScroll({ resetHorizontal: resetHorizontalScroll, resetVertical: true });
  }

  async function selectTable(
    tableName,
    {
      page = 1,
      pageSize = state.previewPageSize,
      resetHorizontalScroll = true,
    } = {}
  ) {
    clearBanner();
    state.selectedTableName = tableName;
    state.previewPage = page;
    state.previewPageSize = pageSize;
    state.rowRequestToken += 1;
    const requestToken = state.rowRequestToken;
    updateSelectedTableStyles();
    setPageSizeControl(pageSize);

    if (selectedTableTitle instanceof HTMLElement) {
      selectedTableTitle.textContent = tableName;
    }
    setSelectedTableMeta("Loading preview rows...");
    hideEmptyState();
    renderGridPlaceholder("Loading columns...", "Loading preview rows...");

    try {
      const payload = await loadRows(tableName, { page, pageSize });
      if (requestToken !== state.rowRequestToken) {
        return;
      }
      renderRows(tableName, payload, { resetHorizontalScroll });
    } catch (error) {
      if (requestToken !== state.rowRequestToken) {
        return;
      }
      setSelectedTableMeta("");
      hidePaginationControls();
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
        await selectTable(table.name, { page: 1, pageSize: state.previewPageSize });
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
      hidePaginationControls();
      return;
    }

    setExplorerHint("Expand a table to inspect its schema, or select one to preview rows.");
    await selectTable(tables[0].name, { page: 1, pageSize: state.previewPageSize });
  }

  function isSplitLayoutEnabled() {
    return !window.matchMedia("(max-width: 960px)").matches;
  }

  function getWorkspaceMetrics() {
    if (!(workspace instanceof HTMLElement) || !(paneSplitter instanceof HTMLElement)) {
      return null;
    }

    const workspaceRect = workspace.getBoundingClientRect();
    const splitterRect = paneSplitter.getBoundingClientRect();
    return {
      left: workspaceRect.left,
      width: workspaceRect.width,
      splitterWidth: splitterRect.width || 12,
    };
  }

  function getCurrentExplorerWidth() {
    const inlineWidth = parseFloat(root.style.getPropertyValue("--explorer-width"));
    if (!Number.isNaN(inlineWidth) && inlineWidth > 0) {
      return inlineWidth;
    }

    const computedWidth = parseFloat(getComputedStyle(root).getPropertyValue("--explorer-width"));
    if (!Number.isNaN(computedWidth) && computedWidth > 0) {
      return computedWidth;
    }

    return MIN_EXPLORER_WIDTH;
  }

  function applyExplorerWidth(rawWidth) {
    const metrics = getWorkspaceMetrics();
    if (metrics === null || !isSplitLayoutEnabled()) {
      return;
    }

    const maxExplorerWidth = Math.max(
      MIN_EXPLORER_WIDTH,
      metrics.width - MIN_DATA_WIDTH - metrics.splitterWidth
    );
    const clampedWidth = Math.min(Math.max(rawWidth, MIN_EXPLORER_WIDTH), maxExplorerWidth);
    root.style.setProperty("--explorer-width", `${clampedWidth}px`);

    if (paneSplitter instanceof HTMLElement) {
      paneSplitter.setAttribute("aria-valuemin", String(MIN_EXPLORER_WIDTH));
      paneSplitter.setAttribute("aria-valuemax", String(Math.round(maxExplorerWidth)));
      paneSplitter.setAttribute("aria-valuenow", String(Math.round(clampedWidth)));
    }
  }

  function resizeExplorerFromPointer(clientX) {
    const metrics = getWorkspaceMetrics();
    if (metrics === null) {
      return;
    }

    applyExplorerWidth(clientX - metrics.left);
  }

  function stopSplitterDrag(pointerId) {
    if (!(paneSplitter instanceof HTMLElement)) {
      return;
    }

    if (pointerId !== null && paneSplitter.hasPointerCapture(pointerId)) {
      paneSplitter.releasePointerCapture(pointerId);
    }

    state.activePointerId = null;
    document.body.classList.remove("is-resizing");
  }

  async function initializeBrowser() {
    clearBanner();
    resetDatabaseState();
    applyExplorerWidth(getCurrentExplorerWidth());

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
        hidePaginationControls();
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
      hidePaginationControls();
      showBanner(error instanceof Error ? error.message : "The application could not finish loading.");
      showEmptyState({
        eyebrow: "Backend Error",
        title: "The browser could not load this session",
        copy: "Check the error banner above, then reload the page or restart the app if the problem persists.",
        showAction: false,
      });
    }
  }

  const savedTheme = window.localStorage.getItem(themeStorageKey) ?? "system";
  applyTheme(savedTheme);

  if (typeof themeMediaQuery.addEventListener === "function") {
    themeMediaQuery.addEventListener("change", () => {
      if ((themeToggle?.dataset.themeChoice ?? "system") === "system") {
        applyTheme("system");
      }
    });
  }

  themeToggle?.addEventListener("click", () => {
    const currentChoice = themeToggle.dataset.themeChoice ?? "system";
    const nextChoice =
      currentChoice === "system"
        ? getResolvedTheme("system") === "dark"
          ? "light"
          : "dark"
        : currentChoice === "dark"
          ? "light"
          : "dark";
    window.localStorage.setItem(themeStorageKey, nextChoice);
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

  paginationPrevButton?.addEventListener("click", async () => {
    if (state.selectedTableName === null || state.previewPage <= 1) {
      return;
    }

    await selectTable(state.selectedTableName, {
      page: state.previewPage - 1,
      pageSize: state.previewPageSize,
      resetHorizontalScroll: false,
    });
  });

  paginationNextButton?.addEventListener("click", async () => {
    if (state.selectedTableName === null || state.previewPage >= state.totalPages) {
      return;
    }

    await selectTable(state.selectedTableName, {
      page: state.previewPage + 1,
      pageSize: state.previewPageSize,
      resetHorizontalScroll: false,
    });
  });

  paginationPageSize?.addEventListener("change", async () => {
    if (!(paginationPageSize instanceof HTMLSelectElement)) {
      return;
    }

    const nextPageSize = Number.parseInt(paginationPageSize.value, 10);
    if (Number.isNaN(nextPageSize) || nextPageSize <= 0) {
      paginationPageSize.value = String(state.previewPageSize);
      return;
    }

    state.previewPageSize = nextPageSize;

    if (state.selectedTableName === null) {
      return;
    }

    await selectTable(state.selectedTableName, {
      page: 1,
      pageSize: nextPageSize,
      resetHorizontalScroll: false,
    });
  });

  paneSplitter?.addEventListener("pointerdown", (event) => {
    if (!isSplitLayoutEnabled()) {
      return;
    }

    event.preventDefault();
    state.activePointerId = event.pointerId;
    paneSplitter.setPointerCapture(event.pointerId);
    document.body.classList.add("is-resizing");
    resizeExplorerFromPointer(event.clientX);
  });

  window.addEventListener("pointermove", (event) => {
    if (state.activePointerId !== event.pointerId) {
      return;
    }

    resizeExplorerFromPointer(event.clientX);
  });

  window.addEventListener("pointerup", (event) => {
    if (state.activePointerId !== event.pointerId) {
      return;
    }

    stopSplitterDrag(event.pointerId);
  });

  window.addEventListener("pointercancel", (event) => {
    if (state.activePointerId !== event.pointerId) {
      return;
    }

    stopSplitterDrag(event.pointerId);
  });

  paneSplitter?.addEventListener("keydown", (event) => {
    if (!isSplitLayoutEnabled()) {
      return;
    }

    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }

    event.preventDefault();
    const direction = event.key === "ArrowLeft" ? -1 : 1;
    applyExplorerWidth(getCurrentExplorerWidth() + direction * SPLITTER_KEYBOARD_STEP);
  });

  window.addEventListener("resize", () => {
    if (!isSplitLayoutEnabled()) {
      stopSplitterDrag(state.activePointerId);
      return;
    }

    applyExplorerWidth(getCurrentExplorerWidth());
  });

  void initializeBrowser();
})();
