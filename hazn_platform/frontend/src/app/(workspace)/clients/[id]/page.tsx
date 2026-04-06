"use client";

/**
 * End-client detail/edit page.
 *
 * Tabs: Overview (brand voice, settings), Credentials (Admin only),
 * Activity (recent workflows).
 *
 * Edit button for brand voice fields.
 * Uses TanStack Query mutations for updates.
 */

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import type {
  EndClient,
  BrandVoice,
  WorkflowRun,
  PaginatedResponse,
} from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-states/empty-state";
import { ArrowLeft, Pencil, Save, X, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function ClientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const clientId = params.id as string;

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editCompetitors, setEditCompetitors] = useState("");

  const { data: client, isLoading: clientLoading } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => api.get<EndClient>(`/workspace/clients/${clientId}/`),
    enabled: !!clientId,
  });

  const { data: brandVoices } = useQuery({
    queryKey: ["clients", clientId, "brand-voices"],
    queryFn: () =>
      api.get<PaginatedResponse<BrandVoice>>(
        `/workspace/clients/${clientId}/brand-voices/`
      ),
    enabled: !!clientId,
  });

  const { data: workflows } = useQuery({
    queryKey: ["workflows", { end_client: clientId }],
    queryFn: () =>
      api.get<PaginatedResponse<WorkflowRun>>(
        `/workspace/workflows/?end_client=${clientId}`
      ),
    enabled: !!clientId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<EndClient>) =>
      api.patch<EndClient>(`/workspace/clients/${clientId}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients", clientId] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Client updated successfully");
      setIsEditing(false);
    },
    onError: () => {
      toast.error("Failed to update client");
    },
  });

  function startEditing() {
    if (client) {
      setEditName(client.name);
      setEditCompetitors((client.competitors || []).join(", "));
      setIsEditing(true);
    }
  }

  function handleSave() {
    updateMutation.mutate({
      name: editName,
      competitors: editCompetitors
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean),
    });
  }

  if (clientLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    );
  }

  if (!client) {
    return (
      <div className="mx-auto max-w-4xl">
        <EmptyState
          title="Client not found"
          description="This client may have been removed or you don't have access."
          emoji="🔍"
          actionLabel="Back to Clients"
          actionHref="/clients"
        />
      </div>
    );
  }

  const activeBrandVoice = brandVoices?.results?.find((bv) => bv.is_active);
  const recentWorkflows = workflows?.results || [];

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/clients")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary text-xl font-bold">
          {client.name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold tracking-tight">{client.name}</h1>
          <p className="text-sm text-muted-foreground">
            Added{" "}
            {formatDistanceToNow(new Date(client.created_at), {
              addSuffix: true,
            })}
          </p>
        </div>
        {!isEditing && (
          <Button
            variant="outline"
            size="sm"
            onClick={startEditing}
            className="rounded-lg"
          >
            <Pencil className="mr-2 h-3 w-3" />
            Edit
          </Button>
        )}
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="credentials">Credentials</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4 mt-4">
          {/* Client details */}
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle className="text-base">Client Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {isEditing ? (
                <>
                  <div className="space-y-2">
                    <Label>Name</Label>
                    <Input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Competitors</Label>
                    <Input
                      value={editCompetitors}
                      onChange={(e) => setEditCompetitors(e.target.value)}
                      placeholder="Comma-separated competitor names"
                    />
                    <p className="text-xs text-muted-foreground">
                      Separate multiple competitors with commas
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={handleSave}
                      disabled={updateMutation.isPending}
                      className="rounded-lg"
                    >
                      {updateMutation.isPending ? (
                        <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                      ) : (
                        <Save className="mr-2 h-3 w-3" />
                      )}
                      Save
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsEditing(false)}
                    >
                      <X className="mr-2 h-3 w-3" />
                      Cancel
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <Label className="text-muted-foreground">Name</Label>
                    <p className="font-medium">{client.name}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Competitors</Label>
                    {client.competitors && client.competitors.length > 0 ? (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {client.competitors.map((comp) => (
                          <Badge key={comp} variant="secondary">
                            {comp}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        No competitors configured
                      </p>
                    )}
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Brand voice */}
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle className="text-base">Brand Voice</CardTitle>
            </CardHeader>
            <CardContent>
              {activeBrandVoice ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-xs">
                      v{activeBrandVoice.version}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      Active
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">
                    {activeBrandVoice.content}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No brand voice configured yet. Add brand guidelines to help
                  agents match this client&apos;s tone and style.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="credentials" className="mt-4">
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle className="text-base">
                Credentials & Connections
              </CardTitle>
            </CardHeader>
            <CardContent>
              <EmptyState
                title="Manage API credentials"
                description="Connect third-party services like Google Analytics, Search Console, and social media platforms."
                emoji="🔑"
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="mt-4">
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle className="text-base">Recent Workflows</CardTitle>
            </CardHeader>
            <CardContent>
              {recentWorkflows.length === 0 ? (
                <EmptyState
                  title="No workflows yet"
                  description="Run your first workflow for this client to see activity here."
                  emoji="🚀"
                  actionLabel="Go to Workflows"
                  actionHref="/workflows"
                />
              ) : (
                <div className="space-y-2">
                  {recentWorkflows.map((run) => (
                    <div
                      key={run.id}
                      className="flex items-center justify-between rounded-lg border px-4 py-3"
                    >
                      <div>
                        <p className="text-sm font-medium">
                          {run.workflow_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(run.created_at), {
                            addSuffix: true,
                          })}
                        </p>
                      </div>
                      <Badge
                        variant={
                          run.status === "completed"
                            ? "default"
                            : run.status === "failed"
                              ? "destructive"
                              : "secondary"
                        }
                      >
                        {run.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
