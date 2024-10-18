
int main(int argc, char *argv[]) {
    int i = 0;
    while (i) {
        if (i) {
            if (i) {
                i = i + 1;
            } else {
                i = i - 1;
            }
        } else {
            if (i) {
                i = i + 1;
            } else {
                i = i + 1;
            }
            continue;
        }
        if (i) {
            i = i + 1;
        } else {
            i = i + 1;
            continue;
        }
    }
    return 0;
}