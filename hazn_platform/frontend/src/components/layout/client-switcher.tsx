"use client";

/**
 * Client switcher dropdown in sidebar.
 *
 * Lists agency's end-clients with "All Clients" at top.
 * Updates useClientScope store to scope dashboard views.
 * Compact when sidebar collapsed.
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import { cn } from "@/lib/utils";
import type { EndClient, PaginatedResponse } from "@/types/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Users } from "lucide-react";

export function ClientSwitcher({ collapsed }: { collapsed: boolean }) {
  const { selectedClientId, setSelectedClient } = useClientScope();

  const { data } = useQuery({
    queryKey: ["clients"],
    queryFn: () =>
      api.get<PaginatedResponse<EndClient>>("/workspace/clients/"),
  });

  const clients = data?.results || [];
  const selectedClient = clients.find((c) => c.id === selectedClientId);

  if (collapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            className="flex h-9 w-full items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
            aria-label="Switch client"
          >
            <div
              className={cn(
                "flex h-6 w-6 items-center justify-center rounded-md text-[10px] font-bold",
                selectedClient
                  ? "bg-primary/10 text-primary"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {selectedClient
                ? selectedClient.name.charAt(0).toUpperCase()
                : <Users className="h-3.5 w-3.5" />}
            </div>
          </button>
        </TooltipTrigger>
        <TooltipContent side="right" sideOffset={8}>
          {selectedClient ? selectedClient.name : "All Clients"}
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <div className="px-1">
      <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-muted-foreground px-2">
        Client
      </label>
      <Select
        value={selectedClientId || "all"}
        onValueChange={(value) =>
          setSelectedClient(value === "all" ? null : value)
        }
      >
        <SelectTrigger className="h-9 w-full rounded-lg text-sm">
          <SelectValue placeholder="All Clients" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">
            <div className="flex items-center gap-2">
              <Users className="h-3.5 w-3.5 text-muted-foreground" />
              <span>All Clients</span>
            </div>
          </SelectItem>
          {clients.map((client) => (
            <SelectItem key={client.id} value={client.id}>
              <div className="flex items-center gap-2">
                <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-[10px] font-bold text-primary">
                  {client.name.charAt(0).toUpperCase()}
                </div>
                <span>{client.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
