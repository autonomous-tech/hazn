"use client";

/**
 * Workflow catalog card with guided trigger dialog.
 *
 * Shows workflow type info (name, description, icon).
 * "Run" button opens a dialog to configure and launch the workflow:
 * - Select end-client
 * - Configure parameters (dynamic)
 * - Estimated cost range
 * - Launch button
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Play, Loader2, DollarSign } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import type {
  EndClient,
  PaginatedResponse,
  WorkflowCatalogItem,
  WorkflowTriggerResponse,
} from "@/types/api";

/**
 * @deprecated Use WorkflowCatalogItem from types/api.ts directly.
 * Kept as alias for backward compatibility with the workflows page.
 */
export type WorkflowType = WorkflowCatalogItem;

interface WorkflowCardProps {
  workflow: WorkflowCatalogItem;
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const router = useRouter();
  const { selectedClientId } = useClientScope();
  const queryClient = useQueryClient();

  const [open, setOpen] = useState(false);
  const [clientId, setClientId] = useState(selectedClientId || "");
  const [params, setParams] = useState<Record<string, string>>({});

  // Fetch end-clients for dropdown
  const { data: clientsData } = useQuery({
    queryKey: ["clients"],
    queryFn: () => api.get<EndClient[] | PaginatedResponse<EndClient>>("/workspace/clients/"),
  });
  const clients = Array.isArray(clientsData) ? clientsData : clientsData?.results ?? [];

  // Trigger workflow mutation
  const triggerMutation = useMutation({
    mutationFn: () =>
      api.post<WorkflowTriggerResponse>("/workspace/workflows/trigger/", {
        workflow_name: workflow.name,
        end_client_id: clientId,
        parameters: params,
      }),
    onSuccess: (data) => {
      toast.success(`Workflow "${workflow.name}" launched`);
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      setOpen(false);
      // Navigate to workflow monitoring page
      if (data.run_id) {
        router.push(`/workflows/${data.run_id}`);
      }
    },
    onError: () => {
      toast.error("Failed to launch workflow");
    },
  });

  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">{workflow.name}</CardTitle>
            <CardDescription className="mt-1 line-clamp-2">
              {workflow.description}
            </CardDescription>
          </div>
          {workflow.estimated_cost != null && (
            <Badge variant="secondary" className="shrink-0 text-xs">
              <DollarSign className="mr-0.5 size-3" />
              ~${workflow.estimated_cost}
            </Badge>
          )}
        </div>
        <div className="mt-2 flex gap-3 text-xs text-muted-foreground">
          <span>{workflow.phases?.length ?? 0} phases</span>
          {workflow.estimated_duration && (
            <span>{workflow.estimated_duration}</span>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="w-full">
              <Play className="size-4" />
              Run Workflow
            </Button>
          </DialogTrigger>

          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Launch {workflow.name}</DialogTitle>
              <DialogDescription>
                Configure and launch this workflow for an end-client.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Client selector */}
              <div className="space-y-2">
                <Label>End-Client</Label>
                <Select value={clientId} onValueChange={setClientId}>
                  <SelectTrigger>
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
              </div>

              {/* Workflow info */}
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>{workflow.phases?.length ?? 0} phases</p>
                {workflow.estimated_duration && (
                  <p>Estimated duration: {workflow.estimated_duration}</p>
                )}
                {workflow.estimated_cost != null ? (
                  <p>Estimated cost: ~${workflow.estimated_cost}</p>
                ) : (
                  <p>No cost data yet -- this will be the first run.</p>
                )}
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={triggerMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                onClick={() => triggerMutation.mutate()}
                disabled={!clientId || triggerMutation.isPending}
              >
                {triggerMutation.isPending ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Launching...
                  </>
                ) : (
                  <>
                    <Play className="size-4" />
                    Launch
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
