#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: ghost-touch-inhibit <eventN> <0|1>\n");
        return 1;
    }

    // Validate event name (security: prevent path traversal)
    if (strncmp(argv[1], "event", 5) != 0) {
        fprintf(stderr, "Invalid device name\n");
        return 1;
    }
    for (const char *p = argv[1] + 5; *p; p++) {
        if (*p < '0' || *p > '9') {
            fprintf(stderr, "Invalid device name\n");
            return 1;
        }
    }

    // Validate value
    if (argv[2][0] != '0' && argv[2][0] != '1') {
        fprintf(stderr, "Value must be 0 or 1\n");
        return 1;
    }
    if (argv[2][1] != '\0') {
        fprintf(stderr, "Value must be 0 or 1\n");
        return 1;
    }

    char path[256];
    int n = snprintf(path, sizeof(path), "/sys/class/input/%s/device/inhibited", argv[1]);
    if (n < 0 || n >= (int)sizeof(path)) {
        fprintf(stderr, "Path too long\n");
        return 1;
    }

    // Verify it's a device (not a symlink trick)
    struct stat st;
    if (stat(path, &st) != 0 || !S_ISREG(st.st_mode)) {
        fprintf(stderr, "Invalid device path\n");
        return 1;
    }

    FILE *f = fopen(path, "w");
    if (!f) {
        perror("fopen");
        return 1;
    }
    fprintf(f, "%s", argv[2]);
    fclose(f);
    return 0;
}
