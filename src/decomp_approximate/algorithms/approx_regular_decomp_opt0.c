#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdarg.h>
#include<time.h>

#define INITIAL_ARRAY_LENGTH 8
#define BUILD_BUFFER_LENGTH 10

#define bag_width(i) bags_array[i].len_ifs + bags_array[i].len_whiles + bags_array[i].include_margorp + bags_array[i].num_nodes

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
    int num_nodes;
    node* nodes;
} bag;

int ntoa(char** dest, node in_node) {
    char *buffer = malloc(sizeof(char) * BUILD_BUFFER_LENGTH);
    int written;
    if (in_node.id == 0) {
        written = snprintf(buffer, BUILD_BUFFER_LENGTH, "%c", in_node.node_type);

    } else {
        written = snprintf(buffer, BUILD_BUFFER_LENGTH, "%c%d", in_node.node_type, in_node.id);
    }
    *dest = buffer;
    return written;
}

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
                memcpy(int_array + i, int_array + i + 1, sizeof(int)*((*current_array_length)-i-1));
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

bag build_bag(int* ifs, int* whiles, int len_ifs, int len_whiles, int include_margorp, int num_nodes, ...) {
    va_list valist;

    bag new_bag;
    
    if (len_ifs > 0) {
        new_bag.ifs = malloc(sizeof(int) * len_ifs);
        memcpy(new_bag.ifs, ifs, sizeof(int) * len_ifs);
    }

    if (len_whiles > 0) { 
        new_bag.whiles = malloc(sizeof(int) * len_whiles);
        memcpy(new_bag.whiles, whiles, sizeof(int) * len_whiles);
    }

    new_bag.len_ifs = len_ifs;
    new_bag.len_whiles = len_whiles;

    new_bag.include_margorp = include_margorp;

    new_bag.num_nodes = num_nodes;

    if (num_nodes > 0) {
        new_bag.nodes = malloc(sizeof(node) * num_nodes);

        va_start(valist, num_nodes);
        node to_add;
        for (int i = 0; i < num_nodes; i++) {
            to_add = va_arg(valist, node);
            memcpy(new_bag.nodes + i, &to_add, sizeof(node));
        }
        va_end(valist);
    }
    return new_bag;
}

char* stringify_nodes(int num_nodes, node* in_nodes) {
    if (num_nodes == 0) {
        char* output = malloc(sizeof(char));
        *output = '\0';
        return output;
    }
    int total_len = 0;
    int* lens = malloc(sizeof(int) * num_nodes);
    char** strings = malloc(sizeof(char*) * num_nodes);
    for (int i = 0; i < num_nodes; i++) {
        lens[i] = ntoa(&(strings[i]), in_nodes[i]);
        //printf("%s %c%d,", strings[i], in_nodes[i].node_type, in_nodes[i].id);
        total_len += lens[i];
    }
    
    char* output = malloc(sizeof(char) * (total_len + num_nodes));
    char* cursor = output;

    for (int i = 0; i < num_nodes; i++) {
        strcpy(cursor, strings[i]);
        free(strings[i]);
        cursor += lens[i];

        if (i + 1 < num_nodes) {
            memset(cursor, ' ', 1);
            cursor += 1;
        }
    }
    //printf("\n");
    free(lens);
    free(strings);

    return output;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <number_of_runs> [<print_all_times?>]\n", argv[0]);
        return 0;
    }

    int num_runs = atoi(argv[1]);
    
    char node_type = '0';
    int id = 0;

    node* node_array = malloc(sizeof(node) * INITIAL_ARRAY_LENGTH);
    int max_len_node_array = INITIAL_ARRAY_LENGTH;
    int current_len_node_array = 0;

    int if_count = 0;
    int while_count = 0;

    int depth = 1;
    int while_depth = 1;

    int max_depth = 1;
    int max_while_depth = 1;
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
                        depth++;
                        break;
                    case 'w':
                        while_count++;
                        depth++;
                        while_depth++;
                        break;

                    case 'f':
                        depth--;
                        break;

                    case 'd':
                        depth--;
                        while_depth--;
                }
                if (depth > max_depth) {
                    max_depth = depth;
                }
                if (while_depth > max_while_depth) {
                    max_while_depth = while_depth;
                }
                continue;
        }
        break;
    }
    if_count *= 2;
    while_count *= 2;

    clock_t total_clocks = 0;
    clock_t *all_clocks = malloc(sizeof(clock_t) * num_runs);

    for (int run = 0; run < num_runs; run++) {
        clock_t start = clock();

        bag *bags_array = malloc(sizeof(bag) * current_len_node_array * 2);
        int num_bags = 0;

        int *ifs;
        if (if_count > 0) {
            ifs = malloc(sizeof(int) * if_count);
        }
        int len_ifs = 0;

        int *whiles;
        if (while_count > 0) {
            whiles = malloc(sizeof(int) * while_count);
        }
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
                    whiles = append_int(whiles, node_array[i].id, &len_whiles, &while_count);
                    whiles = append_int(whiles, -(node_array[i].id), &len_whiles, &while_count);
                    break;

                case 'd':
                    remove_int(whiles, -(node_array[i].id), &len_whiles);
                    remove_int(whiles, node_array[i].id, &len_whiles);
                    break;

                case 'o':
                    bags_array = append_bag(
                                    bags_array, 
                                    build_bag(
                                        ifs, whiles, len_ifs, len_whiles, include_margorp,
                                        1, node_array[i]
                                    ),
                                    &num_bags
                                );
                    break;

                case 'b':
                    bags_array = append_bag(
                                    bags_array, 
                                    build_bag(
                                        ifs, whiles, len_ifs, len_whiles, include_margorp,
                                        1, node_array[i]
                                    ),
                                    &num_bags
                                );
                    break;

                case 'c':
                    bags_array = append_bag(
                                    bags_array, 
                                    build_bag(
                                        ifs, whiles, len_ifs, len_whiles, include_margorp,
                                        1, node_array[i]
                                    ),
                                    &num_bags
                                );
                    break;

                case 'r':
                    bags_array = append_bag(
                                    bags_array, 
                                    build_bag(
                                        ifs, whiles, len_ifs, len_whiles, include_margorp,
                                        1, node_array[i]
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
                                    2, node_array[i], node_array[i+1]
                                ),
                                &num_bags
                            );
            }
            if (node_array[i].node_type == 'p') {
                include_margorp = 1;
            }
        }

        clock_t clocks_taken = (clock() - start);
        total_clocks += clocks_taken;
        all_clocks[run] = clocks_taken;
    
        //double time_taken = clocks_taken / CLOCKS_PER_SEC;

        int max_width = 0;

        for (int i = 0; i < num_bags; i++) {
            if (run + 1 == num_runs) {
                if (bag_width(i) > max_width) {
                    max_width = bag_width(i);
                }

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
                printf("%s\n", stringify_nodes(bags_array[i].num_nodes, bags_array[i].nodes));
            }
            if (bags_array[i].len_ifs > 0) {
                free(bags_array[i].ifs);
            }
            if (bags_array[i].len_whiles > 0) {
                free(bags_array[i].whiles);
            }
            if (bags_array[i].num_nodes > 0) {
                free(bags_array[i].nodes);
            }
        }

        if (if_count > 0) {
            free(ifs);
        }
        if (while_count > 0) {
            free(whiles);
        }
        free(bags_array);
    
        if (run + 1 == num_runs) {
            printf("\n");
            printf("# of Nodes: %d\n",      current_len_node_array);
            printf("Depth: %d\n",           max_depth);
            printf("While Depth: %d\n",     max_while_depth);
            printf("\n");
            printf("# of Bags: %d\n",       num_bags);
            printf("Width: %d\n",           max_width - 1);
            printf("\n");
            printf("Clocks taken: %ld\n",   total_clocks);
            printf("Total runs: %d\n",      num_runs);
            printf("CPS: %ld\n",            CLOCKS_PER_SEC);
            free(node_array);
        }
    }
    if (argc > 2) {
        printf("Times: ");
        for (int run = 0; run < num_runs; run++) {
            printf("%ld ", all_clocks[run]);
        }
    }
    free(all_clocks);
    return 0;
}

// char* build_include(int* ifs, int* whiles, int len_ifs, int len_whiles) {
//     int i;
//     int written;
//     char buffer[BUILD_BUFFER_LENGTH];
//     char *output = NULL;
//     int len_output = 0;

//     for (i = 0; i < len_ifs; i++) {
//         if (ifs[i] > 0) {
//             written = snprintf(buffer, BUILD_BUFFER_LENGTH, "i%d ", ifs[i]);

//         } else {
//             written = snprintf(buffer, BUILD_BUFFER_LENGTH, "f%d ", -ifs[i]);
//         }
//         if (output == NULL) {
//             output = malloc(sizeof(char) * written);
//             //strcpy();
//         }
//     }
//     return output;
// }