"use client";

/**
 * Memory Inspector page.
 *
 * Two view modes via Tabs:
 * - "By End-Client": select client, shows all agent memory blocks for that client
 * - "By Agent Type": select agent type, shows memory blocks for that agent across clients
 *
 * Includes semantic search, inline editing of craft learnings, memory health
 * stats, and bulk select + delete with confirmation.
 */

import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Trash2, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { MemoryBlockCard } from "@/components/memory/memory-block-card";
import { MemorySearch } from "@/components/memory/memory-search";
import { MemoryHealth } from "@/components/memory/memory-health";
import type { EndClient, MemoryBlock, PaginatedResponse } from "@/types/api";

const AGENT_TYPES = [
  { value: "seo_strategist", label: "SEO Strategist" },
  { value: "content_writer", label: "Content Writer" },
  { value: "campaign_manager", label: "Campaign Manager" },
  { value: "audit_analyst", label: "Audit Analyst" },
  { value: "keyword_researcher", label: "Keyword Researcher" },
];

export default function MemoryPage() {
  const { selectedClientId } = useClientScope();
  const queryClient = useQueryClient();

  // View mode
  const [activeTab, setActiveTab] = useState<string>("by-client");

  // Filters
  const [clientFilter, setClientFilter] = useState<string>(
    selectedClientId || ""
  );
  const [agentFilter, setAgentFilter] = useState<string>("");

  // Bulk selection
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Sync client filter when global scope changes
  useMemo(() => {
    if (selectedClientId) {
      setClientFilter(selectedClientId);
    }
  }, [selectedClientId]);

  // Fetch end-clients for dropdown
  const { data: clientsData } = useQuery({
    queryKey: ["clients"],
    queryFn: () =>
      api.get<PaginatedResponse<EndClient>>("/workspace/clients/"),
  });
  const clients = clientsData?.results ?? [];

  // Fetch memory blocks by client
  const {
    data: clientBlocks,
    isLoading: clientBlocksLoading,
  } = useQuery({
    queryKey: ["memory", "blocks", "client", clientFilter],
    queryFn: () =>
      api.get<MemoryBlock[]>(
        `/workspace/memory/blocks/${clientFilter}/`
      ),
    enabled: activeTab === "by-client" && !!clientFilter,
  });

  // Fetch memory blocks by agent type
  const {
    data: agentBlocks,
    isLoading: agentBlocksLoading,
  } = useQuery({
    queryKey: ["memory", "blocks", "agent", agentFilter],
    queryFn: () =>
      api.get<MemoryBlock[]>(
        `/workspace/memory/blocks/?agent_type=${agentFilter}`
      ),
    enabled: activeTab === "by-agent" && !!agentFilter,
  });

  const currentBlocks =
    activeTab === "by-client" ? clientBlocks : agentBlocks;
  const isLoading =
    activeTab === "by-client" ? clientBlocksLoading : agentBlocksLoading;

  // Bulk delete mutation
  const deleteMutation = useMutation({
    mutationFn: (blockIds: string[]) =>
      api.post("/workspace/memory/delete/", { block_ids: blockIds }),
    onSuccess: () => {
      toast.success(`${selectedIds.size} memories deleted`);
      setSelectedIds(new Set());
      setShowDeleteDialog(false);
      queryClient.invalidateQueries({ queryKey: ["memory"] });
    },
    onError: () => {
      toast.error("Failed to delete memories");
    },
  });

  const handleSelectToggle = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleBulkDelete = () => {
    deleteMutation.mutate(Array.from(selectedIds));
  };

  return (
    <div className="space-y-6 p-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="size-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Memory Inspector</h1>
            <p className="text-sm text-muted-foreground">
              View and manage agent memory blocks
            </p>
          </div>
        </div>

        {/* Bulk delete button */}
        {selectedIds.size > 0 && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="size-4" />
            Delete {selectedIds.size} selected
          </Button>
        )}
      </div>

      {/* Memory health stats */}
      {currentBlocks && currentBlocks.length > 0 && (
        <MemoryHealth blocks={currentBlocks} />
      )}

      {/* Semantic search */}
      <MemorySearch
        agentType={activeTab === "by-agent" ? agentFilter : undefined}
        endClientId={activeTab === "by-client" ? clientFilter : undefined}
      />

      {/* View mode tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="by-client">By End-Client</TabsTrigger>
          <TabsTrigger value="by-agent">By Agent Type</TabsTrigger>
        </TabsList>

        {/* By End-Client tab */}
        <TabsContent value="by-client">
          <div className="space-y-4">
            <Select value={clientFilter} onValueChange={setClientFilter}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select end-client" />
              </SelectTrigger>
              <SelectContent>
                {clients.map((client) => (
                  <SelectItem key={client.id} value={client.id}>
                    {client.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {!clientFilter && (
              <EmptyState message="Select an end-client to view their agent memories" />
            )}

            {clientFilter && isLoading && <LoadingSkeleton />}

            {clientFilter &&
              !isLoading &&
              currentBlocks &&
              currentBlocks.length === 0 && (
                <EmptyState message="No memories found for this client. Memories are created when agents run workflows." />
              )}

            {currentBlocks && currentBlocks.length > 0 && (
              <div className="space-y-3">
                {currentBlocks.map((block) => (
                  <MemoryBlockCard
                    key={block.id}
                    block={block}
                    selected={selectedIds.has(block.id)}
                    onSelectToggle={handleSelectToggle}
                  />
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* By Agent Type tab */}
        <TabsContent value="by-agent">
          <div className="space-y-4">
            <Select value={agentFilter} onValueChange={setAgentFilter}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select agent type" />
              </SelectTrigger>
              <SelectContent>
                {AGENT_TYPES.map((agent) => (
                  <SelectItem key={agent.value} value={agent.value}>
                    {agent.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {!agentFilter && (
              <EmptyState message="Select an agent type to view their memories across all clients" />
            )}

            {agentFilter && isLoading && <LoadingSkeleton />}

            {agentFilter &&
              !isLoading &&
              currentBlocks &&
              currentBlocks.length === 0 && (
                <EmptyState message="No memories found for this agent type. Memories are created during workflow execution." />
              )}

            {currentBlocks && currentBlocks.length > 0 && (
              <div className="space-y-3">
                {currentBlocks.map((block) => (
                  <MemoryBlockCard
                    key={block.id}
                    block={block}
                    selected={selectedIds.has(block.id)}
                    onSelectToggle={handleSelectToggle}
                  />
                ))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Delete confirmation dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete memories</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {selectedIds.size} memory block
              {selectedIds.size !== 1 ? "s" : ""}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={deleteMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleBulkDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="size-4" />
                  Delete
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
      <Brain className="mb-4 size-12 text-muted-foreground/40" />
      <p className="max-w-sm text-center text-sm text-muted-foreground">
        {message}
      </p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2 rounded-xl border p-6">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-48" />
          <Skeleton className="h-16 w-full" />
        </div>
      ))}
    </div>
  );
}
