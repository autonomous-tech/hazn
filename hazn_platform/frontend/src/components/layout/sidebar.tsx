"use client";

/**
 * Collapsible sidebar with grouped nav sections.
 *
 * Sections: Overview (Dashboard), Clients (End-Clients), Work (Workflows,
 * Deliverables), Intelligence (Memory Inspector), Settings (bottom).
 *
 * Collapses to icon-only mode via useUIStore().sidebarCollapsed.
 * Active route highlighted with usePathname().
 * Client switcher below main nav.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import { ClientSwitcher } from "./client-switcher";
import {
  LayoutDashboard,
  Users,
  Play,
  FileText,
  Brain,
  Settings,
  ChevronLeft,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface NavItem {
  icon: React.ElementType;
  label: string;
  href: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", href: "/" },
    ],
  },
  {
    label: "Clients",
    items: [
      { icon: Users, label: "End-Clients", href: "/clients" },
    ],
  },
  {
    label: "Work",
    items: [
      { icon: Play, label: "Workflows", href: "/workflows" },
      { icon: FileText, label: "Deliverables", href: "/deliverables" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { icon: Brain, label: "Memory Inspector", href: "/memory" },
    ],
  },
];

function NavLink({
  item,
  isActive,
  collapsed,
}: {
  item: NavItem;
  isActive: boolean;
  collapsed: boolean;
}) {
  const linkContent = (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
        collapsed && "justify-center px-2"
      )}
    >
      <item.icon className="h-4 w-4 shrink-0" />
      {!collapsed && <span>{item.label}</span>}
    </Link>
  );

  if (collapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
        <TooltipContent side="right" sideOffset={8}>
          {item.label}
        </TooltipContent>
      </Tooltip>
    );
  }

  return linkContent;
}

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  function isActive(href: string) {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  }

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r bg-sidebar transition-all duration-200",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo + collapse toggle */}
      <div className="flex h-14 items-center justify-between border-b px-3">
        {!sidebarCollapsed && (
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
              H
            </div>
            <span className="font-bold text-lg text-sidebar-foreground">
              Hazn
            </span>
          </Link>
        )}
        <button
          onClick={toggleSidebar}
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors",
            sidebarCollapsed && "mx-auto"
          )}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <ChevronLeft
            className={cn(
              "h-4 w-4 transition-transform duration-200",
              sidebarCollapsed && "rotate-180"
            )}
          />
        </button>
      </div>

      {/* Nav groups */}
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="mb-4">
            {!sidebarCollapsed && (
              <span className="mb-1 block px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {group.label}
              </span>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.href}
                  item={item}
                  isActive={isActive(item.href)}
                  collapsed={sidebarCollapsed}
                />
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Client switcher */}
      <div className="border-t px-2 py-2">
        <ClientSwitcher collapsed={sidebarCollapsed} />
      </div>

      {/* Settings at bottom */}
      <div className="border-t px-2 py-2">
        <NavLink
          item={{ icon: Settings, label: "Settings", href: "/settings" }}
          isActive={isActive("/settings")}
          collapsed={sidebarCollapsed}
        />
      </div>
    </aside>
  );
}
