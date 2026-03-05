"""
powerbi_ckan_ontario_sources.py

Goal
-----
Create reusable Power Query (M) queries for Power BI Desktop that pull:

- resource_id
- resource_title
- last_validated_date (Ontario "Last Validated Date" field; CKAN extra key: current_as_of)
- tags (flattened into comma-separated string)

From CKAN Action API (Ontario Data Catalogue is CKAN-based).

What this Python file does
--------------------------
1) Stores the M scripts as strings (clean, copy/paste-ready).
2) Writes each M script to its own .m.txt file in an output folder.
3) Prints the scripts so you can copy/paste into Power BI immediately.

How to use in Power BI Desktop
------------------------------
1) Power BI Desktop -> Transform data -> Manage parameters:
   Create TEXT parameters:
     - pBaseUrl                 e.g. https://data.ontario.ca   (if 404, try https://data.ontario.ca/en)
     - pOrganization            
     - pAccessField             access_level   (if no matches, try extras_access_level)
     - pAccessValue             open
     - pLastValidatedExtraKey   current_as_of

2) Power BI Desktop -> Transform data -> New Source -> Blank Query:
   For each generated .m.txt file:
     - Open Advanced Editor
     - Paste the content
     - Name the query exactly as the file name indicates

Recommended query creation order
--------------------------------
1) fnCkanAction
2) fnBuildFq
3) fnExtraValue
4) fnPackageSearchPaged
5) Packages_Filtered
6) Resource_Metadata
"""

from __future__ import annotations

from pathlib import Path

# -----------------------------
# Config: output location
# -----------------------------
OUTPUT_DIR = Path("./powerbi_m_queries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Power Query (M) Scripts
# -----------------------------

M_FN_CKAN_ACTION = r"""
// fnCkanAction(action as text, optional query as nullable record) as any
(action as text, optional query as nullable record) as any =>
let
    // Uses Power BI parameter: pBaseUrl
    Base = Text.TrimEnd(pBaseUrl, "/"),
    q = if query = null then [] else query,
    raw =
        Json.Document(
            Web.Contents(
                Base,
                [
                    RelativePath = "api/3/action/" & action,
                    Query = q,
                    Headers = [Accept="application/json"]
                ]
            )
        ),
    // CKAN returns {success=true/false, result=...}
    result = raw[result]
in
    result
""".strip()

M_FN_BUILD_FQ = r"""
// fnBuildFq(org as text, accessField as text, accessValue as text) as text
(org as text, accessField as text, accessValue as text) as text =>
"organization:" & org & " AND " & accessField & ":" & accessValue
""".strip()

M_FN_EXTRA_VALUE = r"""
// fnExtraValue(extras as any, key as text) as nullable text
// Extras usually looks like a list of records: [{key="...", value="..."}, ...]
(extras as any, key as text) as nullable text =>
let
    list = if extras = null then {} else extras,
    matches = List.Select(list, each Record.HasFields(_, "key") and _[key] = key),
    val = if List.Count(matches) = 0 then null else try Text.From(matches{0}[value]) otherwise null
in
    val
""".strip()

M_FN_PACKAGE_SEARCH_PAGED = r"""
// fnPackageSearchPaged(fq as text, fl as text, optional pageSize as nullable number) as table
// Pulls package_search results in pages to avoid giant payloads.
(fq as text, fl as text, optional pageSize as nullable number) as table =>
let
    PageSize = if pageSize = null then 200 else Number.RoundDown(pageSize),

    // First call: get total count only
    head = fnCkanAction("package_search", [rows="0", fq=fq]),
    total = head[count],

    // Generate page offsets: 0, PageSize, 2*PageSize, ...
    starts = List.Generate(() => 0, each _ < total, each _ + PageSize),

    fetchPage = (start as number) =>
        let
            r = fnCkanAction(
                "package_search",
                [
                    fq = fq,
                    fl = fl,
                    rows = Text.From(PageSize),
                    start = Text.From(start)
                ]
            )
        in
            r[results],

    pages = List.Transform(starts, each fetchPage(_)),
    combined = List.Combine(pages),
    t = Table.FromRecords(combined)
in
    t
""".strip()

M_PACKAGES_FILTERED = r"""
let
    // Uses Power BI parameters:
    // pOrganization, pAccessField, pAccessValue
    fq = fnBuildFq(pOrganization, pAccessField, pAccessValue),

    // Keep it lean: only fields needed to create resource-level rows
    // NOTE: CKAN's fl support can vary by portal; if fl causes issues, remove it and pull full results.
    fl = "id,name,title,tags,extras,resources",

    t = fnPackageSearchPaged(fq, fl, 200)
in
    t
""".strip()

M_RESOURCE_METADATA = r"""
let
    p = Packages_Filtered,

    // last_validated_date: Ontario "Last Validated Date" database key is current_as_of
    // Uses Power BI parameter: pLastValidatedExtraKey (default: current_as_of)
    addLastValidated =
        Table.AddColumn(
            p,
            "last_validated_date",
            each fnExtraValue([extras], pLastValidatedExtraKey),
            type text
        ),

    // tags is a list of records; normalize to single comma-separated string per dataset.
    tagsExpanded = Table.ExpandListColumn(addLastValidated, "tags"),
    tagsNames = Table.ExpandRecordColumn(tagsExpanded, "tags", {"name"}, {"tag"}),

    // Group back to one row per dataset with tag_list, keeping resources
    tagsGrouped =
        Table.Group(
            tagsNames,
            {"id","name","title","last_validated_date","resources"},
            {{"tag_list", each Text.Combine(List.Sort(List.Distinct(List.RemoveNulls([tag]))), ", "), type text}}
        ),

    // Expand resources (one row per resource)
    expandResList = Table.ExpandListColumn(tagsGrouped, "resources"),
    expandResRec =
        Table.ExpandRecordColumn(
            expandResList,
            "resources",
            {"id","name"},
            {"resource_id","resource_title"}
        ),

    // Final output columns (BI-ready)
    out =
        Table.SelectColumns(
            expandResRec,
            {"resource_id","resource_title","last_validated_date","tag_list"}
        )
in
    out
""".strip()

# Optional sanity-check queries (create only if you want them)
M_CHECK_RESOURCE_ROWCOUNT = r"""
let
    n = Table.RowCount(Resource_Metadata)
in
    n
""".strip()

M_CHECK_MISSING_LAST_VALIDATED = r"""
let
    t = Table.SelectRows(Resource_Metadata, each [last_validated_date] = null or Text.Trim([last_validated_date]) = "")
in
    t
""".strip()

SCRIPTS: dict[str, str] = {
    "fnCkanAction.m.txt": M_FN_CKAN_ACTION,
    "fnBuildFq.m.txt": M_FN_BUILD_FQ,
    "fnExtraValue.m.txt": M_FN_EXTRA_VALUE,
    "fnPackageSearchPaged.m.txt": M_FN_PACKAGE_SEARCH_PAGED,
    "Packages_Filtered.m.txt": M_PACKAGES_FILTERED,
    "Resource_Metadata.m.txt": M_RESOURCE_METADATA,
    # Optional:
    "Check_Resource_Metadata_RowCount.m.txt": M_CHECK_RESOURCE_ROWCOUNT,
    "Check_Missing_LastValidated.m.txt": M_CHECK_MISSING_LAST_VALIDATED,
}


def write_scripts(out_dir: Path) -> None:
    for filename, content in SCRIPTS.items():
        path = out_dir / filename
        path.write_text(content + "\n", encoding="utf-8")


def print_scripts() -> None:
    for filename, content in SCRIPTS.items():
        print("\n" + "=" * 80)
        print(filename)
        print("=" * 80)
        print(content)
        print()


if __name__ == "__main__":
    # Writes each M query to: ./powerbi_m_queries/
    write_scripts(OUTPUT_DIR)

    # Also print to console for quick copy/paste
    print(f"Wrote {len(SCRIPTS)} M scripts to: {OUTPUT_DIR.resolve()}")
    print_scripts()

    # Troubleshooting notes (read this if you get 0 rows or API errors):
    #
    # 1) If you see 404 calling the API:
    #    - Change pBaseUrl to https://data.ontario.ca/en  (some portals mount CKAN under language roots)
    #
    # 2) If your filters return 0 packages:
    #    - pOrganization slug might be wrong
    #    - access field might be indexed as extras_access_level rather than access_level
    #
    # 3) If 'fl' causes errors:
    #    - Edit Packages_Filtered to remove fl usage and pull full result objects.