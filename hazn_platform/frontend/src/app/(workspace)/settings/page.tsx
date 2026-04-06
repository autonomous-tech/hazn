"use client";

/**
 * Agency settings page (Admin only).
 *
 * Shows agency name, house style.
 * Team management: list users, invite new member, change role.
 * Basic layout -- placeholder for future expansion.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { Agency, User as UserType } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-states/empty-state";
import {
  Settings,
  UserPlus,
  Shield,
  User,
  Loader2,
  Building2,
} from "lucide-react";
import { toast } from "sonner";

export default function SettingsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"admin" | "member">("member");

  const { data: agency, isLoading: agencyLoading } = useQuery({
    queryKey: ["agency"],
    queryFn: () => api.get<Agency>("/workspace/agency/"),
  });

  const { data: teamMembers, isLoading: teamLoading } = useQuery({
    queryKey: ["team"],
    queryFn: () => api.get<UserType[]>("/workspace/team/"),
  });

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: string }) =>
      api.post("/workspace/team/invite/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team"] });
      toast.success("Invitation sent successfully");
      setInviteOpen(false);
      setInviteEmail("");
    },
    onError: () => {
      toast.error("Failed to send invitation");
    },
  });

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    inviteMutation.mutate({ email: inviteEmail, role: inviteRole });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your agency and team
        </p>
      </div>

      {/* Agency info */}
      <Card className="rounded-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-base">Agency</CardTitle>
          </div>
          <CardDescription>
            Your agency profile and configuration
          </CardDescription>
        </CardHeader>
        <CardContent>
          {agencyLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          ) : agency ? (
            <div className="space-y-4">
              <div>
                <Label className="text-muted-foreground">Agency Name</Label>
                <p className="font-medium">{agency.name}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Slug</Label>
                <p className="text-sm font-mono text-muted-foreground">
                  {agency.slug}
                </p>
              </div>
              {agency.house_style &&
                Object.keys(agency.house_style).length > 0 && (
                  <div>
                    <Label className="text-muted-foreground">House Style</Label>
                    <p className="text-sm">
                      {JSON.stringify(agency.house_style)}
                    </p>
                  </div>
                )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No agency information available
            </p>
          )}
        </CardContent>
      </Card>

      {/* Team management */}
      <Card className="rounded-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-base">Team</CardTitle>
            </div>
            <Button
              size="sm"
              onClick={() => setInviteOpen(true)}
              className="rounded-lg"
            >
              <UserPlus className="mr-2 h-3 w-3" />
              Invite Member
            </Button>
          </div>
          <CardDescription>
            Manage who has access to your workspace
          </CardDescription>
        </CardHeader>
        <CardContent>
          {teamLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-9 w-9 rounded-full" />
                  <div className="space-y-1.5">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-48" />
                  </div>
                </div>
              ))}
            </div>
          ) : teamMembers && teamMembers.length > 0 ? (
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between rounded-lg border px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary text-sm font-medium">
                      {(member.name || member.email)
                        .charAt(0)
                        .toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium">
                        {member.name || member.email}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {member.email}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      member.agency_role === "admin" ? "default" : "secondary"
                    }
                  >
                    {member.agency_role === "admin" ? (
                      <Shield className="mr-1 h-3 w-3" />
                    ) : (
                      <User className="mr-1 h-3 w-3" />
                    )}
                    {member.agency_role}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No team members"
              description="Invite colleagues to collaborate in your workspace"
              emoji="👋"
              actionLabel="Invite First Member"
              onAction={() => setInviteOpen(true)}
            />
          )}
        </CardContent>
      </Card>

      {/* Invite dialog */}
      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="rounded-xl">
          <DialogHeader>
            <DialogTitle>Invite Team Member</DialogTitle>
            <DialogDescription>
              Send an invitation to join your workspace
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleInvite} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="invite-email">Email</Label>
              <Input
                id="invite-email"
                type="email"
                placeholder="colleague@agency.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Role</Label>
              <Select
                value={inviteRole}
                onValueChange={(value) =>
                  setInviteRole(value as "admin" | "member")
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="member">
                    <div className="flex items-center gap-2">
                      <User className="h-3 w-3" />
                      Member
                    </div>
                  </SelectItem>
                  <SelectItem value="admin">
                    <div className="flex items-center gap-2">
                      <Shield className="h-3 w-3" />
                      Admin
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Admins can manage team, credentials, and agency settings.
                Members can view dashboard, trigger workflows, and view
                deliverables.
              </p>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setInviteOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={inviteMutation.isPending}
                className="rounded-lg"
              >
                {inviteMutation.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Send Invitation
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
