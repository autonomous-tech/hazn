"use client";

/**
 * Share dialog for deliverables.
 *
 * "Generate Share Link" button creates a public share link.
 * Displays URL with copy-to-clipboard. Shows expiry date.
 * Admin can revoke existing links.
 */

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Copy, Check, Link2, Loader2, Trash2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
interface ShareLink {
  token: string;
  share_url: string;
  expires_at: string;
}

interface ShareDialogProps {
  deliverableId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Whether user is an admin (can revoke links) */
  isAdmin?: boolean;
}

export function ShareDialog({
  deliverableId,
  open,
  onOpenChange,
  isAdmin = false,
}: ShareDialogProps) {
  const [shareLink, setShareLink] = useState<ShareLink | null>(null);
  const [copied, setCopied] = useState(false);

  const generateMutation = useMutation({
    mutationFn: () =>
      api.post<ShareLink>(
        `/workspace/deliverables/${deliverableId}/share/`
      ),
    onSuccess: (data) => {
      setShareLink(data);
      toast.success("Share link generated");
    },
    onError: () => toast.error("Failed to generate share link"),
  });

  const revokeMutation = useMutation({
    mutationFn: () =>
      api.delete(
        `/workspace/deliverables/${deliverableId}/share/${shareLink?.token}/`
      ),
    onSuccess: () => {
      setShareLink(null);
      toast.success("Share link revoked");
    },
    onError: () => toast.error("Failed to revoke share link"),
  });

  const handleCopy = async () => {
    if (shareLink?.share_url) {
      await navigator.clipboard.writeText(shareLink.share_url);
      setCopied(true);
      toast.success("Link copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleClose = (open: boolean) => {
    if (!open) {
      setShareLink(null);
      setCopied(false);
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Link2 className="size-5" />
            Share Deliverable
          </DialogTitle>
          <DialogDescription>
            Generate a public link to share this deliverable. Anyone with the
            link can view it without logging in.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {!shareLink ? (
            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="w-full"
            >
              {generateMutation.isPending ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Link2 className="size-4" />
                  Generate Share Link
                </>
              )}
            </Button>
          ) : (
            <div className="space-y-3">
              {/* Share URL with copy */}
              <div className="flex gap-2">
                <Input
                  value={shareLink.share_url}
                  readOnly
                  className="text-xs"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <Check className="size-4 text-green-500" />
                  ) : (
                    <Copy className="size-4" />
                  )}
                </Button>
              </div>

              {/* Expiry info */}
              <p className="text-xs text-muted-foreground">
                Expires{" "}
                {formatDistanceToNow(new Date(shareLink.expires_at), {
                  addSuffix: true,
                })}
              </p>

              {/* Revoke button (admin only) */}
              {isAdmin && (
                <Button
                  variant="outline"
                  size="sm"
                  className="text-destructive"
                  onClick={() => revokeMutation.mutate()}
                  disabled={revokeMutation.isPending}
                >
                  {revokeMutation.isPending ? (
                    <Loader2 className="size-3 animate-spin" />
                  ) : (
                    <Trash2 className="size-3" />
                  )}
                  Revoke Link
                </Button>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleClose(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
