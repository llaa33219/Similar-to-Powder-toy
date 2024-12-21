import pygame
import sys

class Simulation:
    def __init__(self, width=240, height=135, scale=4):
        self.width = width
        self.height = height
        self.scale = scale
        self.running = True

        # 파티클 데이터 2차원 배열
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # 파티클 색상
        self.colors = {
            0: (0,0,0),
            1: (194,178,128),
            2: (0,0,255),
            3: (100,100,100)
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width*self.scale, self.height*self.scale))
        pygame.display.set_caption("Powder Simulation (Python)")
        
        # 프레임 카운트: 어느 정도 시간 흐름에 따라 검사 순서를 바꾸기 위해
        self.frame_count = 0

    def spawn_particle(self, x, y, ptype):
        # 특정 (x,y)에 ptype 파티클 생성
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = ptype

    def update_particles(self):
        # 매 프레임마다 파티클 상태 업데이트
        # frame_count를 이용해 홀수 프레임에서는 왼->오, 짝수 프레임에서는 오->왼 순서로 검사
        left_first = (self.frame_count % 2 == 0)

        for y in range(self.height-2, -1, -1):
            for x in range(self.width):
                p = self.grid[y][x]
                if p == 1:
                    # 모래
                    if y+1 < self.height and self.grid[y+1][x] == 0:
                        self.grid[y+1][x] = 1
                        self.grid[y][x] = 0
                    else:
                        # 아래 막혔으면 대각
                        if y+1 < self.height:
                            if left_first:
                                # 왼쪽 먼저
                                if x > 0 and self.grid[y+1][x-1] == 0:
                                    self.grid[y+1][x-1] = 1
                                    self.grid[y][x] = 0
                                elif x < self.width-1 and self.grid[y+1][x+1] == 0:
                                    self.grid[y+1][x+1] = 1
                                    self.grid[y][x] = 0
                            else:
                                # 오른쪽 먼저
                                if x < self.width-1 and self.grid[y+1][x+1] == 0:
                                    self.grid[y+1][x+1] = 1
                                    self.grid[y][x] = 0
                                elif x > 0 and self.grid[y+1][x-1] == 0:
                                    self.grid[y+1][x-1] = 1
                                    self.grid[y][x] = 0
                elif p == 2:
                    # 물
                    if y+1 < self.height and self.grid[y+1][x] == 0:
                        self.grid[y+1][x] = 2
                        self.grid[y][x] = 0
                    else:
                        # 아래 막혔으니 좌우, 대각선 검사
                        moved = False
                        # 좌우 검사 순서: 프레임에 따라 바뀜
                        if left_first:
                            # 왼쪽 먼저, 그 다음 오른쪽
                            side_checks = [(x-1,y),(x+1,y)]
                        else:
                            # 오른쪽 먼저, 그 다음 왼쪽
                            side_checks = [(x+1,y),(x-1,y)]

                        for (sx, sy) in side_checks:
                            if 0 <= sx < self.width and self.grid[sy][sx] == 0:
                                self.grid[sy][sx] = 2
                                self.grid[y][x] = 0
                                moved = True
                                break

                        if not moved:
                            # 대각선 아래 검사
                            if left_first:
                                diag_checks = [(x-1,y+1),(x+1,y+1)]
                            else:
                                diag_checks = [(x+1,y+1),(x-1,y+1)]

                            for (dx, dy) in diag_checks:
                                if 0 <= dx < self.width and dy < self.height and self.grid[dy][dx] == 0:
                                    self.grid[dy][dx] = 2
                                    self.grid[y][x] = 0
                                    break
                # 돌(3)은 움직이지 않음
                # 빈공간(0)은 처리 없음

        self.frame_count += 1

    def draw(self):
        self.screen.fill((0,0,0))
        for y in range(self.height):
            for x in range(self.width):
                p = self.grid[y][x]
                color = self.colors[p]
                pygame.draw.rect(self.screen, color, (x*self.scale, y*self.scale, self.scale, self.scale))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    cx, cy = mx//self.scale, my//self.scale
                    mods = pygame.key.get_mods()
                    shift_pressed = (mods & pygame.KMOD_SHIFT) != 0

                    if event.button == 1:
                        # 왼클릭
                        if shift_pressed:
                            # 돌(3)
                            self.spawn_particle(cx, cy, 3)
                        else:
                            # 모래(1)
                            self.spawn_particle(cx, cy, 1)
                    elif event.button == 3:
                        # 오른쪽 클릭: 물(2)
                        self.spawn_particle(cx, cy, 2)

            self.update_particles()
            self.draw()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
