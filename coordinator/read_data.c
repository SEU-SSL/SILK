#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#define MAP_SIZE_POW2 20
#define MAP_SIZE (1 << MAP_SIZE_POW2)

typedef uint32_t u32;

struct edge_info
{
	u32 seed_id;
	u32 hit_count;
};

typedef struct edge_info edge_info_t;
edge_info_t *edge_statistics;

int main()
{
	char *shm_key = "coordinator";
	int fd = shm_open(shm_key, O_RDWR, 0666);
	if (fd <= -1)
	{
		fprintf(stderr, "Failed to open shared memory region: %d\n", errno);
		_exit(-1);
	}
	edge_statistics = (edge_info_t *)mmap(NULL, MAP_SIZE * sizeof(edge_info_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
	if (edge_statistics == MAP_FAILED)
	{
		fprintf(stderr, "Failed to mmap shared memory region\n");
		_exit(-1);
	}

	for (u32 i = 0; i < MAP_SIZE; i++)
	{
		if (edge_statistics[i].hit_count)
		{
			printf("%d,%d,%d\n", i, edge_statistics[i].seed_id, edge_statistics[i].hit_count);
		}
	}
}
