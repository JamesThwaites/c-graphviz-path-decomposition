#include<stdio.h>

typedef struct {
    char node_type;
    char t;
    unsigned short int weight;
    int id;
} nice_node;

int main(int argc, char *argv[]) {
    char node_type = '0';
    int id = 0;

    printf("%d\n", sizeof(char));
    
    while (1) {
        switch (scanf("%c%d ", &node_type, &id)) {
            case 1:
                printf("p:%c\n", node_type);
                continue;
            case 2:
                printf("p:%c id:%d\n", node_type, id);
                continue;
        }
        break;
    }    
    return 0;
}