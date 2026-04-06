"use client";

/**
 * Semantic memory search input.
 *
 * Debounced search input (300ms) that queries the memory search API.
 * Displays results as memory-block-cards. Clear button to reset.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, X, Loader2 } from "lucide-react";

import { api } from "@/lib/api";
import { useDebounce } from "@/hooks/use-debounce";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { MemoryBlockCard } from "@/components/memory/memory-block-card";
import type { MemorySearchResult } from "@/types/api";

interface MemorySearchProps {
  /** Optional agent type filter for search */
  agentType?: string;
  /** Optional end-client ID filter for search */
  endClientId?: string;
}

export function MemorySearch({ agentType, endClientId }: MemorySearchProps) {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ["memory", "search", debouncedQuery, agentType, endClientId],
    queryFn: () => {
      const params = new URLSearchParams({ query: debouncedQuery });
      if (agentType) params.set("agent_type", agentType);
      if (endClientId) params.set("end_client_id", endClientId);
      return api.get<MemorySearchResult>(
        `/workspace/memory/search/?${params.toString()}`
      );
    },
    enabled: debouncedQuery.length >= 2,
  });

  const handleClear = () => {
    setQuery("");
  };

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search memories semantically..."
          className="pl-9 pr-9"
        />
        {query && (
          <Button
            variant="ghost"
            size="icon-xs"
            className="absolute right-2 top-1/2 -translate-y-1/2"
            onClick={handleClear}
          >
            <X className="size-3" />
          </Button>
        )}
      </div>

      {/* Loading state */}
      {isLoading && debouncedQuery.length >= 2 && (
        <div className="flex items-center justify-center py-8 text-muted-foreground">
          <Loader2 className="mr-2 size-4 animate-spin" />
          Searching memories...
        </div>
      )}

      {/* Search results */}
      {searchResults && searchResults.results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {searchResults.results.length} result
            {searchResults.results.length !== 1 ? "s" : ""} for &ldquo;
            {searchResults.query}&rdquo;
          </p>
          {searchResults.results.map((block) => (
            <MemoryBlockCard key={block.id} block={block} />
          ))}
        </div>
      )}

      {/* No results */}
      {searchResults &&
        searchResults.results.length === 0 &&
        debouncedQuery.length >= 2 && (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No memories found for &ldquo;{searchResults.query}&rdquo;
          </p>
        )}
    </div>
  );
}
