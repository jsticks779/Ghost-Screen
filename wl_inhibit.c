#include <gdk/gdk.h>
#include <gdk/gdkwayland.h>
#include <wayland-client.h>
#include <string.h>
#include <stdio.h>
#include "zwp_ksh_client.h"

struct inhibitor_state {
    struct wl_display *display;
    struct wl_surface *surface;
    struct wl_seat *seat;
    struct zwp_keyboard_shortcuts_inhibitor_v1 *inhibitor;
    struct wl_registry *registry;
    int pending_roundtrip;
    int active;
};

static void registry_global(void *data, struct wl_registry *registry,
                            uint32_t name, const char *interface, uint32_t version) {
    (void)registry;
    struct inhibitor_state *state = (struct inhibitor_state *)data;
    if (strcmp(interface, "zwp_keyboard_shortcuts_inhibit_manager_v1") == 0) {
        struct zwp_keyboard_shortcuts_inhibit_manager_v1 *mgr =
            wl_registry_bind(registry, name,
                             &zwp_keyboard_shortcuts_inhibit_manager_v1_interface, 1);
        if (mgr && state->surface && state->seat) {
            state->inhibitor = zwp_keyboard_shortcuts_inhibit_manager_v1_inhibit_shortcuts(
                mgr, state->surface, state->seat);
        }
        state->pending_roundtrip = 1;
    }
}

static void registry_global_remove(void *data, struct wl_registry *registry,
                                   uint32_t name) {
    (void)data; (void)registry; (void)name;
}

static const struct wl_registry_listener registry_listener = {
    registry_global,
    registry_global_remove
};

static void inhibitor_active(void *data, struct zwp_keyboard_shortcuts_inhibitor_v1 *inhibitor) {
    (void)inhibitor;
    struct inhibitor_state *state = (struct inhibitor_state *)data;
    state->active = 1;
}

static void inhibitor_inactive(void *data, struct zwp_keyboard_shortcuts_inhibitor_v1 *inhibitor) {
    (void)inhibitor;
    struct inhibitor_state *state = (struct inhibitor_state *)data;
    state->active = 0;
}

static const struct zwp_keyboard_shortcuts_inhibitor_v1_listener inhibitor_listener = {
    inhibitor_active,
    inhibitor_inactive
};

void ghost_inhibit_stop(struct inhibitor_state *state);

struct inhibitor_state *ghost_inhibit_start(void) {
    struct inhibitor_state *state = calloc(1, sizeof(struct inhibitor_state));
    if (!state) return NULL;

    gdk_display_manager_get();
    GdkDisplay *gdk_display = gdk_display_get_default();
    if (!gdk_display) {
        free(state); return NULL;
    }

    state->display = gdk_wayland_display_get_wl_display(gdk_display);
    if (!state->display) {
        free(state); return NULL;
    }

    GdkScreen *screen = gdk_display_get_default_screen(gdk_display);
    if (!screen) {
        free(state); return NULL;
    }

    GList *windows = gdk_screen_get_toplevel_windows(screen);
    GdkWindow *ghost_win = NULL;
    for (GList *l = windows; l; l = l->next) {
        GdkWindow *w = GDK_WINDOW(l->data);
        if (gdk_window_is_visible(w)) {
            ghost_win = w;
            break;
        }
    }
    if (!ghost_win && windows && windows->data)
        ghost_win = GDK_WINDOW(windows->data);
    if (!ghost_win) {
        free(state); return NULL;
    }

    state->surface = gdk_wayland_window_get_wl_surface(ghost_win);
    if (!state->surface) {
        free(state); return NULL;
    }

    GdkSeat *gdk_seat = gdk_display_get_default_seat(gdk_display);
    if (!gdk_seat) {
        free(state); return NULL;
    }
    state->seat = gdk_wayland_seat_get_wl_seat(gdk_seat);
    if (!state->seat) {
        free(state); return NULL;
    }

    state->registry = wl_display_get_registry(state->display);
    wl_registry_add_listener(state->registry, &registry_listener, state);
    wl_display_roundtrip(state->display);
    wl_display_roundtrip(state->display);

    if (state->inhibitor) {
        zwp_keyboard_shortcuts_inhibitor_v1_add_listener(state->inhibitor, &inhibitor_listener, state);
        wl_display_roundtrip(state->display);
        return state;
    }

    ghost_inhibit_stop(state);
    return NULL;
}

void ghost_inhibit_stop(struct inhibitor_state *state) {
    if (!state) return;
    if (state->inhibitor) {
        zwp_keyboard_shortcuts_inhibitor_v1_destroy(state->inhibitor);
    }
    if (state->registry) {
        wl_registry_destroy(state->registry);
    }
    if (state->display) {
        wl_display_flush(state->display);
    }
    free(state);
}

int ghost_inhibit_is_active(struct inhibitor_state *state) {
    return state ? state->active : 0;
}
