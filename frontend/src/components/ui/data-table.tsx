/**
 * DataTable — Tableau paginé réutilisable
 * Wrapper simple (sans Tanstack Table pour l'instant) avec :
 *   - Colonnes typées
 *   - Pagination côté client ou côté serveur
 *   - État vide intégré
 *   - Loading skeleton
 *   - Tri simple par colonne
 */

"use client";

import { useState, useMemo } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "@/components/ui/empty-state";
import { RadarSpinner } from "@/components/ui/radar-spinner";
import { cn } from "@/lib/utils";
import { Database } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface DataTableColumn<T> {
  /** Clé unique de la colonne */
  key: string;
  /** En-tête */
  header: string;
  /** Rendu de la cellule */
  render?: (row: T) => React.ReactNode;
  /** Accès à la valeur brute (pour le tri) */
  accessor?: (row: T) => string | number | null | undefined;
  /** Activer le tri sur cette colonne */
  sortable?: boolean;
  /** Classes CSS additionnelles pour la colonne */
  className?: string;
  /** Largeur fixe */
  width?: string;
}

interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  /** Clé unique par row (pour React key) */
  rowKey: (row: T) => string | number;
  loading?: boolean;
  emptyMessage?: string;
  /** Pagination côté serveur fournie par le parent */
  pagination?: PaginationConfig;
  className?: string;
  /** Callback clic sur une ligne */
  onRowClick?: (row: T) => void;
}

// ─── Composant ────────────────────────────────────────────────────────────────

export function DataTable<T>({
  columns,
  data,
  rowKey,
  loading = false,
  emptyMessage = "Aucune donnée disponible.",
  pagination,
  className,
  onRowClick,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // ─── Tri côté client (si pas de pagination serveur) ─────────────────────
  const sortedData = useMemo(() => {
    if (!sortKey || pagination) return data;
    const col = columns.find((c) => c.key === sortKey);
    if (!col?.accessor) return data;

    return [...data].sort((a, b) => {
      const aVal = col.accessor!(a) ?? "";
      const bVal = col.accessor!(b) ?? "";
      const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir, columns, pagination]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  // ─── Pagination côté client ──────────────────────────────────────────────
  const [clientPage, setClientPage] = useState(1);
  const pageSize = pagination?.pageSize ?? 25;
  const currentPage = pagination?.page ?? clientPage;
  const total = pagination?.total ?? data.length;
  const totalPages = Math.ceil(total / pageSize);

  const displayData = pagination
    ? sortedData
    : sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const onPageChange = pagination?.onPageChange ?? setClientPage;

  // ─── Render ──────────────────────────────────────────────────────────────
  return (
    <div className={cn("rounded-lg border border-border/50 overflow-hidden", className)}>
      <div className="overflow-x-auto custom-scrollbar">
        <Table>
          <TableHeader>
            <TableRow className="border-border/50 hover:bg-transparent">
              {columns.map((col) => (
                <TableHead
                  key={col.key}
                  style={col.width ? { width: col.width } : undefined}
                  className={cn(
                    "text-xs font-medium text-muted-foreground uppercase tracking-wider font-data py-3",
                    col.sortable && "cursor-pointer select-none hover:text-foreground",
                    col.className
                  )}
                  onClick={col.sortable ? () => handleSort(col.key) : undefined}
                >
                  <span className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && (
                      <span className="opacity-50">
                        {sortKey === col.key ? (
                          sortDir === "asc" ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )
                        ) : (
                          <ChevronsUpDown className="w-3 h-3" />
                        )}
                      </span>
                    )}
                  </span>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {/* ── Loading ───────────────────────────────────────────────── */}
            {loading && (
              <TableRow>
                <TableCell colSpan={columns.length} className="py-12">
                  <div className="flex justify-center">
                    <RadarSpinner size={36} label="Chargement…" />
                  </div>
                </TableCell>
              </TableRow>
            )}

            {/* ── Empty state ───────────────────────────────────────────── */}
            {!loading && displayData.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} className="p-0">
                  <EmptyState
                    message={emptyMessage}
                    className="py-10"
                  />
                </TableCell>
              </TableRow>
            )}

            {/* ── Rows ──────────────────────────────────────────────────── */}
            {!loading &&
              displayData.map((row) => (
                <TableRow
                  key={rowKey(row)}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  className={cn(
                    "border-border/30 hover:bg-accent/30 transition-colors",
                    onRowClick && "cursor-pointer"
                  )}
                >
                  {columns.map((col) => (
                    <TableCell
                      key={col.key}
                      className={cn("py-3 text-sm", col.className)}
                    >
                      {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? "—")}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </div>

      {/* ── Pagination ────────────────────────────────────────────────────── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-border/50 bg-card/50">
          <span className="text-xs text-muted-foreground font-data">
            {Math.min((currentPage - 1) * pageSize + 1, total)}–{Math.min(currentPage * pageSize, total)} / {total}
          </span>

          <div className="flex items-center gap-1">
            <button
              id="table-prev-page"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="px-2 py-1 rounded text-xs text-muted-foreground hover:text-foreground
                         hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Préc.
            </button>

            {/* Pages visibles */}
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page =
                totalPages <= 5
                  ? i + 1
                  : currentPage <= 3
                  ? i + 1
                  : currentPage >= totalPages - 2
                  ? totalPages - 4 + i
                  : currentPage - 2 + i;
              return (
                <button
                  key={page}
                  id={`table-page-${page}`}
                  onClick={() => onPageChange(page)}
                  className={cn(
                    "w-7 h-7 rounded text-xs transition-colors",
                    currentPage === page
                      ? "bg-radar/15 text-radar border border-radar/30"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent"
                  )}
                >
                  {page}
                </button>
              );
            })}

            <button
              id="table-next-page"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-2 py-1 rounded text-xs text-muted-foreground hover:text-foreground
                         hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Suiv.
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
