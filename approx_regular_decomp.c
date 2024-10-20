#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdarg.h>

#define INITIAL_ARRAY_LENGTH 8
#define BUILD_BUFFER_LENGTH 10

typedef struct {
    char node_type;
    int id;
} node;

typedef struct {
    int* ifs;
    int len_ifs;
    int* whiles;
    int len_whiles;
    int include_margorp;
    char* blocks;
} bag;

int has_entry_node(node in_node) {
    switch (in_node.node_type) {
        case 'i':
            return 1;
        
        case 'w':
            return 1;
        
        case 'o':
            return 1;
        
        case 'b':
            return 1;
        
        case 'c':
            return 1;
        
        case 'r':
            return 1;
    }
    return 0;
}
        
int has_exit_node(node in_node) {
    switch (in_node.node_type) {
        case 'p':
            return 1;
        
        case 'f':
            return 1;
        
        case 'd':
            return 1;
        
        case 'o':
            return 1;
    }
    return 0;
}

int remove_int(int* int_array, int to_remove, int* current_array_length) {
    for (int i = (*current_array_length) - 1; i >= 0; i--) {
        if (int_array[i] == to_remove) {
            if (i != *current_array_length - 1) {
                memcpy(int_array + i*sizeof(int), int_array + (i+1)*sizeof(int), (*current_array_length)-i);
            } else {
                int_array[i] = 0;
            }
            (*current_array_length)--;
            return 1;
        }
    }
    return 0;
}

int* append_int(int* int_array, int to_append, int* current_array_length, int* array_max_length) {
    if (*current_array_length == *array_max_length) {
        (*array_max_length) *= 2;
        int_array = realloc(int_array, sizeof(int) * (*array_max_length));
    }
    int_array[*current_array_length] = to_append;
    (*current_array_length)++;
    return int_array;
}

node* append_node(node* node_array, node to_append, int* current_array_length, int* array_max_length) {
    if (*current_array_length == *array_max_length) {
        (*array_max_length) *= 2;
        node_array = realloc(node_array, sizeof(node) * (*array_max_length));
    }
    node_array[*current_array_length] = to_append;
    (*current_array_length)++;
    return node_array;
}

bag* append_bag(bag* bag_array, bag to_append, int* current_array_length) {
    bag_array[*current_array_length] = to_append;
    (*current_array_length)++;
    return bag_array;
}

bag build_bag(int* ifs, int* whiles, int len_ifs, int len_whiles, int include_margorp, int num_blocks, ...) {
    va_list valist;

    bag new_bag;
    new_bag.ifs = malloc(sizeof(int) * len_ifs);
    memcpy(new_bag.ifs, ifs, sizeof(int) * len_ifs);

    new_bag.whiles = malloc(sizeof(int) * len_whiles);
    memcpy(new_bag.whiles, whiles, sizeof(int) * len_whiles);

    new_bag.len_ifs = len_ifs;
    new_bag.len_whiles = len_whiles;

    new_bag.include_margorp = include_margorp;


    int total_len = 0;
    int* lens = malloc(sizeof(int) * num_blocks);
    va_start(valist, num_blocks);
    for (int i = 0; i < num_blocks; i++) {
        lens[i] = strlen(va_arg(valist, char*));
        total_len += lens[i];
    }
    va_end(valist);

    new_bag.blocks = malloc(sizeof(char) * (total_len + num_blocks));

    char* current_arg;
    char* cursor = new_bag.blocks;

    va_start(valist, num_blocks);
    for (int i = 0; i < num_blocks; i++) {
        current_arg = va_arg(valist, char*);
        strcpy(cursor, current_arg);
        free(current_arg);
        cursor += lens[i] * sizeof(char);

        if (i + 1 < num_blocks) {
            memset(cursor, ' ', 1);
            cursor += sizeof(char);
        }
    }
    va_end(valist);
    free(lens);

    return new_bag;
}

char* stringify_nodes(int num_blocks, node* in_nodes) {

    return NULL;
}

char* ntoa(node in_node) {
    char *buffer = malloc(sizeof(char) * BUILD_BUFFER_LENGTH);
    if (in_node.id == 0) {
        snprintf(buffer, BUILD_BUFFER_LENGTH, "%c", in_node.node_type);

    } else {
        snprintf(buffer, BUILD_BUFFER_LENGTH, "%c%d", in_node.node_type, in_node.id);
    }
    return buffer;
}

char* build_include(int* ifs, int* whiles, int len_ifs, int len_whiles) {
    int i;
    int written;
    char buffer[BUILD_BUFFER_LENGTH];
    char *output = NULL;
    int len_output = 0;

    for (i = 0; i < len_ifs; i++) {
        if (ifs[i] > 0) {
            written = snprintf(buffer, BUILD_BUFFER_LENGTH, "i%d ", ifs[i]);

        } else {
            written = snprintf(buffer, BUILD_BUFFER_LENGTH, "f%d ", -ifs[i]);
        }
        if (output == NULL) {
            output = malloc(sizeof(char) * written);
            //strcpy();
        }
    }
    return output;
}

int main(int argc, char *argv[]) {
    char node_type = '0';
    int id = 0;

    node* node_array = malloc(sizeof(node) * INITIAL_ARRAY_LENGTH);
    int max_len_node_array = INITIAL_ARRAY_LENGTH;
    int current_len_node_array = 0;

    int if_count = 0;
    int while_count = 0;
    //printf("%d\n", sizeof(char));
    while (1) {
        switch (scanf("%c%d ", &node_type, &id)) {
            case 1:
                node_array = append_node(node_array, (node) {node_type, 0}, &current_len_node_array, &max_len_node_array);
                continue;
            case 2:
                if (node_type == 'i' || node_type == 'f' || node_type == 'r') {
                    id++;
                }
                node_array = append_node(node_array, (node) {node_type, id}, &current_len_node_array, &max_len_node_array);
                switch (node_type) {
                    case 'i':
                        if_count++;
                        break;
                    case 'w':
                        while_count++;
                        break;
                }
                continue;
        }
        break;
    }
    if_count *= 2;
    while_count *= 2;

    //printf("num_nodes: %d\n", current_len_node_array);

    bag *bags_array = malloc(sizeof(bag) * current_len_node_array);
    int num_bags = 0;

    int *ifs = malloc(sizeof(int) * if_count);
    int len_ifs = 0;

    int *whiles = malloc(sizeof(int) * while_count);
    int len_whiles = 0;

    int include_margorp = 0;

    for (int i = 0; i < current_len_node_array; i++) {
        //printf("%c%d\n", node_array[i].node_type, node_array[i].id);
        if (node_array[i].node_type == 'm') {
            continue;
        }
        //printf("%c\n", node_array[i].node_type);
        switch (node_array[i].node_type) {
            case 'i':
                ifs = append_int(ifs, node_array[i].id, &len_ifs, &if_count);
                ifs = append_int(ifs, -(node_array[i].id), &len_ifs, &if_count);
                break;

            case 'f':
                remove_int(ifs, -(node_array[i].id), &len_ifs);
                remove_int(ifs, node_array[i].id, &len_ifs);
                break;

            case 'w':
                whiles = append_int(whiles, -(node_array[i].id), &len_whiles, &while_count);
                whiles = append_int(whiles, node_array[i].id, &len_whiles, &while_count);
                break;

            case 'd':
                remove_int(whiles, node_array[i].id, &len_whiles);
                remove_int(whiles, -(node_array[i].id), &len_whiles);
                break;

            case 'o':
                bags_array = append_bag(
                                bags_array, 
                                build_bag(
                                    ifs, whiles, len_ifs, len_whiles, include_margorp,
                                    1, ntoa(node_array[i])
                                ),
                                &num_bags
                            );
                break;

            case 'b':
                bags_array = append_bag(
                                bags_array, 
                                build_bag(
                                    ifs, whiles, len_ifs, len_whiles, include_margorp,
                                    1, ntoa(node_array[i])
                                ),
                                &num_bags
                            );
                break;

            case 'c':
                bags_array = append_bag(
                                bags_array, 
                                build_bag(
                                    ifs, whiles, len_ifs, len_whiles, include_margorp,
                                    1, ntoa(node_array[i])
                                ),
                                &num_bags
                            );
                break;

            case 'r':
                bags_array = append_bag(
                                bags_array, 
                                build_bag(
                                    ifs, whiles, len_ifs, len_whiles, include_margorp,
                                    1, ntoa(node_array[i])
                                ),
                                &num_bags
                            );
                break;
        }
        if (has_exit_node(node_array[i]) && has_entry_node(node_array[i+1])) {
            bags_array = append_bag(
                            bags_array, 
                            build_bag(
                                ifs, whiles, len_ifs, len_whiles, include_margorp,
                                2, ntoa(node_array[i]), ntoa(node_array[i+1])
                            ),
                            &num_bags
                        );
        }
        if (node_array[i].node_type == 'p') {
            include_margorp = 1;
        }
    }

    printf("num_bags: %d\n", num_bags);

    for (int i = 0; i < num_bags; i++) {
        if (bags_array[i].include_margorp) {
            printf("m ");
        }
        for (int j = 0; j < bags_array[i].len_ifs; j++) {
            if (bags_array[i].ifs[j] > 0) {
                printf("i%d ", bags_array[i].ifs[j]);

            } else {
                printf("f%d ", -(bags_array[i].ifs[j]));
            }
        }
        for (int j = 0; j < bags_array[i].len_whiles; j++) {
            if (bags_array[i].whiles[j] > 0) {
                printf("w%d ", bags_array[i].whiles[j]);

            } else {
                printf("d%d ", -(bags_array[i].whiles[j]));
            }
        }
        printf("%s\n", bags_array[i].blocks);

        free(bags_array[i].ifs);
        free(bags_array[i].whiles);
        free(bags_array[i].blocks);
    }

    free(ifs);
    free(whiles);
    free(bags_array);
    free(node_array);
    return 0;
}