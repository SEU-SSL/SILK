import pwn
import os


class Constraint:
    def __init__(self):
        self.constraint_id = 0
        self.left_id = 0
        self.left_hit = 0
        self.left_seed = 0
        self.right_id = 0
        self.right_hit = 0
        self.right_seed = 0
        self.solve_times = 0
        self.stuck_pr = 0
        # stuck_state:0,1,2 (number of branches executed)
        self.stuck_state = 0


class Eval:
    def __init__(self, constraints, edge_id_dict):
        self.constraints = constraints
        self.edge_id_dict = edge_id_dict

    def read_memory(self):
        read_script = "read_data"
        content = pwn.process(os.path.join(os.getcwd(), read_script)).recvall()
        for line in content.split(b'\n'):
            if not line:
                continue
            line_arr = line.split(b",")
            edge_id = int(line_arr[0])
            seed_id = int(line_arr[1])
            hit_count = int(line_arr[2])
            index = self.edge_id_dict[edge_id]
            constraint = self.constraints[index]
            solve_times = constraint.solve_times
            if constraint.left_id == edge_id:
                constraint.left_seed = seed_id
                constraint.left_hit = hit_count
                right_hit = constraint.right_hit
                if right_hit == 0:
                    pr = hit_count - solve_times
                    constraint.stuck_state = 1
                else:
                    diff = abs(hit_count - right_hit) - solve_times
                    pr = round(float(diff) / (hit_count + right_hit))
                    constraint.stuck_state = 2
            else:
                constraint.right_seed = seed_id
                constraint.right_hit = hit_count
                left_hit = constraint.left_hit
                if left_hit == 0:
                    pr = hit_count - solve_times
                    constraint.stuck_state = 1
                else:
                    diff = abs(hit_count - left_hit) - solve_times
                    pr = round(float(diff) / (hit_count + left_hit))
                    constraint.stuck_state = 2
            constraint.stuck_pr = pr

    def add_to_queue(self):
        seed_queue = []
        for constraint in self.constraints:
            if constraint.stuck_state == 1:
                if constraint.left_hit != 0:
                    edge_id = constraint.left_id
                    seed_id = constraint.left_seed
                else:
                    edge_id = constraint.right_id
                    seed_id = constraint.right_seed
                seed_queue.append({
                    "edge_id": edge_id,
                    "stuck_pr": constraint.stuck_pr,
                    "solve_times": constraint.solve_times,
                    "seed_id": seed_id
                })
        if len(seed_queue) != 0:
            return self.delete_repeat(seed_queue)
        else:
            for constraint in self.constraints:
                if constraint.stuck_state == 2:
                    if constraint.left_hit < constraint.right_hit:
                        edge_id = constraint.left_id
                        seed_id = constraint.left_seed
                    else:
                        edge_id = constraint.right_id
                        seed_id = constraint.right_seed
                    seed_queue.append({
                        "edge_id": edge_id,
                        "stuck_pr": constraint.stuck_pr,
                        "solve_times": constraint.solve_times,
                        "seed_id": seed_id
                    })
            return self.delete_repeat(seed_queue)

    def get_selected_seeds(self):
        self.read_memory()
        seed_queue = self.sort_queue(self.add_to_queue())
        return seed_queue

    def get_seed_name(self, seed_id, fp):
        for i in os.listdir(fp):
            ids = i.split(b',')[0]
            if seed_id in ids:
                seed_name = os.path.join(fp, i)
                break
        return seed_name

    def sort_queue(self, seed_queue):
        return sorted(seed_queue, key=lambda q: (q["solve_times"], -q["stuck_pr"]))

    def delete_repeat(self, seed_queue):
        selected_seeds = []
        selected_ids = []
        for seed in seed_queue:
            if seed["seed_id"] not in selected_ids:
                selected_seeds.append(seed)
                selected_ids.append(seed["seed_id"])
        return selected_seeds
