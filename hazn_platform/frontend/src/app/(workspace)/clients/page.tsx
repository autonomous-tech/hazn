"use client";

/**
 * End-client list page.
 *
 * Card layout on mobile, table-like on desktop.
 * Each client: name, brand voice summary, active workflows count, last activity.
 * "Add Client" button (Admin only).
 * Empty state with illustration for new agencies.
 */

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { EndClient, PaginatedResponse } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/empty-states/empty-state";
import { Plus, Users, ArrowRight, Loader2 } from "lucide-react";
import { toast } from "sonner";

function ClientCardSkeleton() {
  return (
    <Card className="rounded-xl">
      <CardContent className="p-5">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-48" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function AddClientDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const createMutation = useMutation({
    mutationFn: (data: { name: string }) =>
      api.post<EndClient>("/workspace/clients/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Client created successfully");
      onOpenChange(false);
      setName("");
    },
    onError: () => {
      toast.error("Failed to create client");
    },
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createMutation.mutateAsync({ name });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-xl">
        <DialogHeader>
          <DialogTitle>Add New Client</DialogTitle>
          <DialogDescription>
            Create a new end-client to manage their brand, workflows, and
            deliverables.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="client-name">Client Name</Label>
            <Input
              id="client-name"
              placeholder="Enter client name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="rounded-lg"
            >
              {isSubmitting && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create Client
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function ClientsPage() {
  const { user } = useAuth();
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: () =>
      api.get<PaginatedResponse<EndClient>>("/workspace/clients/"),
  });

  const clients = data?.results || [];

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">End-Clients</h1>
          <p className="text-sm text-muted-foreground">
            Manage your agency&apos;s client portfolio
          </p>
        </div>
        <Button
          className="rounded-lg"
          onClick={() => setAddDialogOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Client
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <ClientCardSkeleton />
          <ClientCardSkeleton />
          <ClientCardSkeleton />
        </div>
      ) : clients.length === 0 ? (
        <EmptyState
          title="No clients yet"
          description="Add your first end-client to start managing their brand, run workflows, and produce deliverables."
          emoji="👥"
          actionLabel="Add Your First Client"
          onAction={() => setAddDialogOpen(true)}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {clients.map((client) => (
            <Link key={client.id} href={`/clients/${client.id}`}>
              <Card className="rounded-xl transition-shadow hover:shadow-md cursor-pointer">
                <CardContent className="p-5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary font-bold">
                      {client.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold truncate">{client.name}</h3>
                      <p className="text-xs text-muted-foreground">
                        Added{" "}
                        {formatDistanceToNow(new Date(client.created_at), {
                          addSuffix: true,
                        })}
                      </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                  {client.competitors && client.competitors.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {client.competitors.slice(0, 3).map((comp) => (
                        <Badge
                          key={comp}
                          variant="secondary"
                          className="text-xs"
                        >
                          {comp}
                        </Badge>
                      ))}
                      {client.competitors.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{client.competitors.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <AddClientDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
      />
    </div>
  );
}
