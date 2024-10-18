
int main(int argc, char *argv[]) {
    int i = 0;
    do {
        
        if (i) {
            if (i) {
                if (i) {
                    i = i + 1;
                }
            } else {
                i = i + 1;
            }
            i = i + 1;
        }
        else {
            if (i) {
                i = i + 1;
            } else {
                i = i + 1;
            }
        }
    } while (i);
    if (i) {
        i = i + 1;
    }
    return 0;
}