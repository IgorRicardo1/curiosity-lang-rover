"""Simulador visual do Rover usando Pygame."""

from __future__ import annotations

from array import array
from dataclasses import dataclass
import math
import random
from typing import Sequence

import pygame

from vm.estado import Mapa, NOMES_DIRECAO, TAMANHO_MAPA
from vm.isa import Instrucao
from vm.maquina import ErroVM, EventoVM, MaquinaVirtual

# Bloco "tune ao vivo": os valores abaixo mudam bastante o feeling da demo.
CELL_SIZE = 40
GRID_PADDING = 24
TOP_HUD = 86
BOTTOM_HUD = 74
FPS = 60
MOVE_DURATION = 0.20
TURN_DURATION = 0.11
CAMERA_SHAKE_DURATION = 0.28
CAMERA_SHAKE_PX = 8

COR_CEU_TOPO = (16, 12, 24)
COR_CEU_BASE = (44, 30, 54)
COR_MARTE_AREIA = (97, 63, 52)
COR_MARTE_AREIA_ALT = (108, 70, 58)
COR_GRID = (158, 112, 92)
COR_OBSTACULO = (81, 56, 49)
COR_OBSTACULO_HL = (135, 89, 75)
COR_TEXTO = (239, 235, 228)
COR_TEXTO_SEC = (202, 192, 182)
COR_STATUS_OK = (109, 216, 150)
COR_STATUS_ALERTA = (255, 137, 116)
COR_STATUS_EXEC = (121, 190, 255)
COR_ROVER = (108, 193, 255)
COR_ROVER_SOMBRA = (24, 31, 44, 95)
COR_ROVER_BORDA = (18, 30, 44)
COR_TRILHA = (141, 214, 255, 120)


@dataclass
class EstadoPlayback:
    indice_evento: int = 0
    progresso: float = 0.0
    pausado: bool = False
    mensagem_status: str = "Inicializando missao..."


@dataclass
class Particula:
    x: float
    y: float
    vx: float
    vy: float
    vida: float
    vida_total: float
    tamanho: float
    cor: tuple[int, int, int]


class SistemaAudio:
    def __init__(self):
        self.habilitado = False
        self.mutado = False
        self._sons: dict[str, pygame.mixer.Sound] = {}
        self._som_ambiente: pygame.mixer.Sound | None = None
        self._canal_ambiente: pygame.mixer.Channel | None = None
        self._inicializar()

    def _inicializar(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.habilitado = True
            self._sons = {
                "boot": self._criar_tom(360, 0.09, 0.18, onda="sine"),
                "move": self._criar_tom(185, 0.08, 0.15, onda="triangle"),
                "turn": self._criar_tom(280, 0.07, 0.13, onda="square"),
                "collision": self._criar_tom(72, 0.30, 0.23, onda="noise"),
                "success": self._criar_efeito_sucesso(),
            }
            self._som_ambiente = self._criar_ambiente()
        except pygame.error:
            self.habilitado = False
            self._sons = {}
            self._som_ambiente = None

    def _criar_tom(self, freq: float, duracao: float, volume: float, onda: str) -> pygame.mixer.Sound:
        # Audio procedural para nao depender de arquivos .wav externos na apresentação.
        taxa = 22050
        total = max(1, int(taxa * duracao))
        dados = array("h")
        rng = random.Random(101)

        for i in range(total):
            t = i / taxa
            fase = 2.0 * math.pi * freq * t
            if onda == "square":
                base = 1.0 if math.sin(fase) >= 0 else -1.0
            elif onda == "triangle":
                base = 2.0 * abs(2.0 * ((freq * t) - math.floor(freq * t + 0.5))) - 1.0
            elif onda == "noise":
                base = rng.uniform(-1.0, 1.0)
            else:
                base = math.sin(fase)

            ataque = min(1.0, i / max(1, int(total * 0.10)))
            release = min(1.0, (total - i) / max(1, int(total * 0.25)))
            env = min(ataque, release)
            amostra = int(32767 * volume * env * base)
            dados.append(max(-32767, min(32767, amostra)))

        return pygame.mixer.Sound(buffer=dados.tobytes())

    def _criar_efeito_sucesso(self) -> pygame.mixer.Sound:
        taxa = 22050
        duracao = 0.52
        total = int(taxa * duracao)
        dados = array("h")

        for i in range(total):
            t = i / taxa
            freq = 220 + 180 * t + 110 * (t**2)
            fase = 2.0 * math.pi * freq * t
            base = 0.62 * math.sin(fase) + 0.38 * math.sin(2.0 * fase)
            ataque = min(1.0, i / max(1, int(total * 0.08)))
            release = min(1.0, (total - i) / max(1, int(total * 0.30)))
            env = min(ataque, release)
            amostra = int(32767 * 0.18 * env * base)
            dados.append(max(-32767, min(32767, amostra)))

        return pygame.mixer.Sound(buffer=dados.tobytes())

    def _criar_ambiente(self) -> pygame.mixer.Sound:
        taxa = 22050
        duracao = 3.2
        total = int(taxa * duracao)
        dados = array("h")

        for i in range(total):
            t = i / taxa
            base = (
                0.55 * math.sin(2.0 * math.pi * 43 * t)
                + 0.35 * math.sin(2.0 * math.pi * 57 * t)
                + 0.10 * math.sin(2.0 * math.pi * 87 * t)
            )
            onda = base * (0.70 + 0.30 * math.sin(2.0 * math.pi * 0.20 * t))
            amostra = int(32767 * 0.08 * onda)
            dados.append(max(-32767, min(32767, amostra)))

        return pygame.mixer.Sound(buffer=dados.tobytes())

    def iniciar_ambiente(self) -> None:
        if not self.habilitado or self.mutado or self._som_ambiente is None:
            return
        self._canal_ambiente = self._som_ambiente.play(loops=-1)
        if self._canal_ambiente is not None:
            self._canal_ambiente.set_volume(0.22)

    def tocar(self, nome: str) -> None:
        if not self.habilitado or self.mutado:
            return
        som = self._sons.get(nome)
        if som is not None:
            som.play()

    def alternar_mudo(self) -> bool:
        self.mutado = not self.mutado
        if self._canal_ambiente is not None:
            self._canal_ambiente.set_volume(0.0 if self.mutado else 0.22)
        return self.mutado

    def encerrar(self) -> None:
        if self._canal_ambiente is not None:
            self._canal_ambiente.stop()


def executar_simulacao_visual(
    programa: list[Instrucao], mapa: Mapa | None = None, titulo: str = "Curiosity-L Rover"
) -> MaquinaVirtual:
    mapa_execucao = mapa or Mapa()
    eventos: list[EventoVM] = []
    vm = MaquinaVirtual(programa, mapa_execucao, ao_evento=eventos.append)

    try:
        vm.executar()
    except ErroVM as e:
        vm.parado = True
        vm.mensagem = str(e)
        eventos.append(
            EventoVM(
                tipo="erro",
                x=vm.rover.x,
                y=vm.rover.y,
                direcao=vm.rover.direcao,
                mensagem=vm.mensagem,
            )
        )

    if vm.parado and vm.mensagem and (not eventos or eventos[-1].mensagem != vm.mensagem):
        eventos.append(
            EventoVM(
                tipo="erro",
                x=vm.rover.x,
                y=vm.rover.y,
                direcao=vm.rover.direcao,
                mensagem=vm.mensagem,
            )
        )

    _rodar_janela(eventos, mapa_execucao, titulo)
    return vm


def _rodar_janela(eventos: Sequence[EventoVM], mapa: Mapa, titulo: str) -> None:
    if not eventos:
        raise ValueError("Nao ha eventos para renderizar no simulador visual")

    pygame.init()
    sistema_audio = SistemaAudio()
    try:
        largura = GRID_PADDING * 2 + CELL_SIZE * TAMANHO_MAPA
        altura = TOP_HUD + CELL_SIZE * TAMANHO_MAPA + BOTTOM_HUD
        try:
            screen = pygame.display.set_mode((largura, altura))
        except pygame.error as e:
            raise ValueError(
                "Nao foi possivel abrir a janela Pygame neste ambiente. Use --no-visual."
            ) from e
        pygame.display.set_caption(titulo)

        clock = pygame.time.Clock()
        fonte_titulo = pygame.font.Font(None, 40)
        fonte_base = pygame.font.Font(None, 30)
        fonte_status = pygame.font.Font(None, 32)
        fonte_msg = pygame.font.Font(None, 52)
        sprites = _criar_sprites_rover(int(CELL_SIZE * 0.73))
        estrelas = _gerar_estrelas(largura, TOP_HUD + 48, 70)
        particulas: list[Particula] = []

        estado = EstadoPlayback()
        estado.mensagem_status = _status_evento(eventos[0], "Inicializando missao...")
        tempo_total = 0.0
        shake_restante = 0.0
        em_execucao = True

        sistema_audio.tocar("boot")
        sistema_audio.iniciar_ambiente()
        shake_restante = max(shake_restante, _aplicar_evento(eventos[0], particulas, sistema_audio))

        while em_execucao:
            # Loop principal da cena (entrada + simulacao + render por frame).
            dt = clock.tick(FPS) / 1000.0
            tempo_total += dt

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    em_execucao = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        em_execucao = False
                    elif evento.key == pygame.K_r:
                        estado = EstadoPlayback()
                        estado.mensagem_status = "Replay iniciado"
                        particulas.clear()
                        shake_restante = 0.0
                        sistema_audio.tocar("boot")
                    elif evento.key == pygame.K_SPACE:
                        estado.pausado = not estado.pausado
                        estado.mensagem_status = "Pausado" if estado.pausado else "Execucao retomada"
                    elif evento.key == pygame.K_m:
                        mutado = sistema_audio.alternar_mudo()
                        estado.mensagem_status = "Audio mutado" if mutado else "Audio ativado"

            origem = eventos[estado.indice_evento]
            destino = origem

            if not estado.pausado and estado.indice_evento < len(eventos) - 1:
                destino = eventos[estado.indice_evento + 1]
                duracao = MOVE_DURATION if _eh_movimento(origem, destino) else TURN_DURATION
                estado.progresso += dt / duracao
                if estado.progresso >= 1.0:
                    estado.indice_evento += 1
                    estado.progresso = 0.0
                    origem = eventos[estado.indice_evento]
                    destino = origem
                    estado.mensagem_status = _status_evento(origem, estado.mensagem_status)
                    shake_restante = max(
                        shake_restante,
                        _aplicar_evento(origem, particulas, sistema_audio),
                    )
            else:
                estado.mensagem_status = _status_evento(origem, estado.mensagem_status)

            x_rover = _interpolar(origem.x, destino.x, estado.progresso)
            y_rover = _interpolar(origem.y, destino.y, estado.progresso)
            direcao = destino.direcao if destino is not origem else origem.direcao
            trilha = _coletar_trilha(eventos, estado.indice_evento, (x_rover, y_rover))

            _atualizar_particulas(particulas, dt)
            camera_offset = _camera_offset(dt, shake_restante)
            if shake_restante > 0.0:
                shake_restante = max(0.0, shake_restante - dt)

            _desenhar_cena(
                screen=screen,
                tempo_total=tempo_total,
                fonte_titulo=fonte_titulo,
                fonte_base=fonte_base,
                fonte_status=fonte_status,
                fonte_msg=fonte_msg,
                sprites=sprites,
                estrelas=estrelas,
                mapa=mapa,
                trilha=trilha,
                particulas=particulas,
                x_rover=x_rover,
                y_rover=y_rover,
                direcao=direcao,
                status=estado.mensagem_status,
                progresso=(estado.indice_evento + 1) / len(eventos),
                pausado=estado.pausado,
                finalizado=estado.indice_evento == len(eventos) - 1,
                audio_habilitado=sistema_audio.habilitado,
                audio_mutado=sistema_audio.mutado,
                camera_offset=camera_offset,
            )
            pygame.display.flip()
    finally:
        sistema_audio.encerrar()
        pygame.quit()


def _desenhar_cena(
    screen: pygame.Surface,
    tempo_total: float,
    fonte_titulo: pygame.font.Font,
    fonte_base: pygame.font.Font,
    fonte_status: pygame.font.Font,
    fonte_msg: pygame.font.Font,
    sprites: Sequence[pygame.Surface],
    estrelas: Sequence[tuple[int, int, int, float]],
    mapa: Mapa,
    trilha: Sequence[tuple[float, float]],
    particulas: Sequence[Particula],
    x_rover: float,
    y_rover: float,
    direcao: int,
    status: str,
    progresso: float,
    pausado: bool,
    finalizado: bool,
    audio_habilitado: bool,
    audio_mutado: bool,
    camera_offset: tuple[int, int],
) -> None:
    _desenhar_fundo_ceu(screen, tempo_total, estrelas)
    _desenhar_grid(screen, mapa, camera_offset)
    _desenhar_trilha(screen, trilha, camera_offset)
    _desenhar_particulas(screen, particulas, camera_offset)
    _desenhar_rover(screen, sprites[direcao], x_rover, y_rover, tempo_total, camera_offset)
    _desenhar_hud(
        screen=screen,
        tempo_total=tempo_total,
        fonte_titulo=fonte_titulo,
        fonte_base=fonte_base,
        fonte_status=fonte_status,
        direcao=direcao,
        x_rover=x_rover,
        y_rover=y_rover,
        status=status,
        progresso=progresso,
        pausado=pausado,
        audio_habilitado=audio_habilitado,
        audio_mutado=audio_mutado,
    )
    _desenhar_msg_final(screen, tempo_total, fonte_msg, status, finalizado)


def _desenhar_fundo_ceu(
    screen: pygame.Surface, tempo_total: float, estrelas: Sequence[tuple[int, int, int, float]]
) -> None:
    largura, altura = screen.get_size()
    for y in range(altura):
        t = y / max(1, altura - 1)
        r = int(COR_CEU_TOPO[0] * (1 - t) + COR_CEU_BASE[0] * t)
        g = int(COR_CEU_TOPO[1] * (1 - t) + COR_CEU_BASE[1] * t)
        b = int(COR_CEU_TOPO[2] * (1 - t) + COR_CEU_BASE[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (largura, y))

    for x, y, raio, fase in estrelas:
        brilho = 120 + int(100 * (0.5 + 0.5 * math.sin(tempo_total * 1.7 + fase)))
        cor = (brilho, brilho, min(255, brilho + 30))
        pygame.draw.circle(screen, cor, (x, y), raio)


def _desenhar_grid(screen: pygame.Surface, mapa: Mapa, camera_offset: tuple[int, int]) -> None:
    origem_x = GRID_PADDING + camera_offset[0]
    origem_y = TOP_HUD + camera_offset[1]
    largura = CELL_SIZE * TAMANHO_MAPA
    altura = CELL_SIZE * TAMANHO_MAPA

    for y in range(TAMANHO_MAPA):
        for x in range(TAMANHO_MAPA):
            base_cor = COR_MARTE_AREIA if (x + y) % 2 == 0 else COR_MARTE_AREIA_ALT
            rect = pygame.Rect(
                origem_x + x * CELL_SIZE,
                origem_y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, base_cor, rect)
            pygame.draw.rect(screen, COR_GRID, rect, 1)

            if mapa.tem_obstaculo(x, y):
                centro = rect.center
                pygame.draw.circle(screen, COR_OBSTACULO, centro, CELL_SIZE // 3)
                pygame.draw.circle(
                    screen,
                    COR_OBSTACULO_HL,
                    (centro[0] - 4, centro[1] - 4),
                    CELL_SIZE // 7,
                )
                pygame.draw.circle(screen, COR_GRID, centro, CELL_SIZE // 3, 1)

    pygame.draw.rect(screen, COR_GRID, pygame.Rect(origem_x, origem_y, largura, altura), 2)


def _desenhar_trilha(
    screen: pygame.Surface,
    trilha: Sequence[tuple[float, float]],
    camera_offset: tuple[int, int],
) -> None:
    if len(trilha) < 2:
        return

    pontos = [_para_pixel(pos[0], pos[1], camera_offset) for pos in trilha]
    trilha_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(trilha_surface, COR_TRILHA, False, pontos, 4)
    for ponto in pontos:
        pygame.draw.circle(trilha_surface, COR_TRILHA, ponto, 5)
    screen.blit(trilha_surface, (0, 0))


def _desenhar_particulas(
    screen: pygame.Surface, particulas: Sequence[Particula], camera_offset: tuple[int, int]
) -> None:
    if not particulas:
        return

    camada = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for p in particulas:
        px, py = _para_pixel(p.x, p.y, camera_offset)
        alpha = int(200 * max(0.0, p.vida / max(0.001, p.vida_total)))
        cor = (p.cor[0], p.cor[1], p.cor[2], alpha)
        pygame.draw.circle(camada, cor, (px, py), max(1, int(p.tamanho)))
    screen.blit(camada, (0, 0))


def _desenhar_rover(
    screen: pygame.Surface,
    sprite: pygame.Surface,
    x_celula: float,
    y_celula: float,
    tempo_total: float,
    camera_offset: tuple[int, int],
) -> None:
    centro = _para_pixel(x_celula, y_celula, camera_offset)

    sombra_surface = pygame.Surface((70, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra_surface, COR_ROVER_SOMBRA, sombra_surface.get_rect())
    sombra_rect = sombra_surface.get_rect(center=(centro[0], centro[1] + 14))
    screen.blit(sombra_surface, sombra_rect)

    glow = pygame.Surface((88, 88), pygame.SRCALPHA)
    alpha = 35 + int(25 * (0.5 + 0.5 * math.sin(tempo_total * 5.2)))
    pygame.draw.circle(glow, (122, 212, 255, alpha), (44, 44), 30)
    glow_rect = glow.get_rect(center=centro)
    screen.blit(glow, glow_rect)

    rect = sprite.get_rect(center=centro)
    screen.blit(sprite, rect)


def _desenhar_hud(
    screen: pygame.Surface,
    tempo_total: float,
    fonte_titulo: pygame.font.Font,
    fonte_base: pygame.font.Font,
    fonte_status: pygame.font.Font,
    direcao: int,
    x_rover: float,
    y_rover: float,
    status: str,
    progresso: float,
    pausado: bool,
    audio_habilitado: bool,
    audio_mutado: bool,
) -> None:
    largura, altura = screen.get_size()

    topo = pygame.Rect(0, 0, largura, TOP_HUD)
    pygame.draw.rect(screen, (14, 12, 22), topo)
    pygame.draw.line(screen, (66, 58, 78), (0, TOP_HUD - 1), (largura, TOP_HUD - 1), 2)

    titulo = fonte_titulo.render("Curiosity-L Mission Control", True, COR_TEXTO)
    screen.blit(titulo, (GRID_PADDING, 12))

    progresso = max(0.0, min(1.0, progresso))
    bar_rect = pygame.Rect(GRID_PADDING, 52, largura - GRID_PADDING * 2, 16)
    pygame.draw.rect(screen, (62, 54, 72), bar_rect, border_radius=8)
    fill_w = int(bar_rect.width * progresso)
    if fill_w > 0:
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
        pygame.draw.rect(screen, (109, 183, 255), fill_rect, border_radius=8)

    progresso_txt = fonte_base.render(f"Progresso: {int(progresso * 100)}%", True, COR_TEXTO_SEC)
    screen.blit(progresso_txt, (bar_rect.x, bar_rect.y + 20))

    direcao_txt = fonte_base.render(
        f"Posicao ({round(x_rover, 2)}, {round(y_rover, 2)}) | Direcao {NOMES_DIRECAO[direcao]}",
        True,
        COR_TEXTO_SEC,
    )
    screen.blit(direcao_txt, (GRID_PADDING, TOP_HUD + CELL_SIZE * TAMANHO_MAPA + 12))

    status_rect = pygame.Rect(largura - 328, TOP_HUD + CELL_SIZE * TAMANHO_MAPA + 4, 304, 30)
    cor_status = _cor_status(status)
    pulso = 0.80 + 0.20 * (0.5 + 0.5 * math.sin(tempo_total * 4.0))
    cor_pulso = (
        min(255, int(cor_status[0] * pulso)),
        min(255, int(cor_status[1] * pulso)),
        min(255, int(cor_status[2] * pulso)),
    )
    pygame.draw.rect(screen, (25, 22, 34), status_rect, border_radius=8)
    pygame.draw.rect(screen, cor_pulso, status_rect, 2, border_radius=8)

    status_txt = fonte_status.render(status, True, cor_pulso)
    screen.blit(status_txt, (status_rect.x + 8, status_rect.y + 5))

    audio_label = "Audio indisponivel"
    if audio_habilitado:
        audio_label = "Audio mutado" if audio_mutado else "Audio ativo"
    audio_txt = fonte_base.render(audio_label, True, COR_TEXTO_SEC)
    screen.blit(audio_txt, (largura - 190, 12))

    controles = "SPACE pausa/retoma  |  R replay  |  M audio  |  ESC sair"
    controle_txt = fonte_base.render(controles, True, COR_TEXTO_SEC)
    screen.blit(controle_txt, (GRID_PADDING, altura - 30))

    if pausado:
        pausa_txt = fonte_status.render("PAUSADO", True, COR_STATUS_EXEC)
        screen.blit(pausa_txt, (largura - 128, 44))


def _desenhar_msg_final(
    screen: pygame.Surface,
    tempo_total: float,
    fonte_msg: pygame.font.Font,
    status: str,
    finalizado: bool,
) -> None:
    if not finalizado or "colisao" in status.lower() or "saiu do mapa" in status.lower():
        return

    texto = "MISSAO FINALIZADA"
    alpha = 150 + int(80 * (0.5 + 0.5 * math.sin(tempo_total * 2.8)))
    msg_surface = fonte_msg.render(texto, True, (255, 238, 214))
    glow = pygame.Surface((msg_surface.get_width() + 30, msg_surface.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.rect(glow, (95, 173, 255, alpha // 2), glow.get_rect(), border_radius=14)
    glow_rect = glow.get_rect(center=(screen.get_width() // 2, TOP_HUD + 35))
    msg_rect = msg_surface.get_rect(center=glow_rect.center)
    screen.blit(glow, glow_rect)
    screen.blit(msg_surface, msg_rect)


def _status_evento(evento: EventoVM, status_atual: str) -> str:
    if evento.mensagem:
        return evento.mensagem
    if evento.tipo == "inicio":
        return "Missao iniciada"
    if evento.tipo == "giro":
        return "Ajustando orientacao"
    if evento.tipo == "movimento":
        return "Navegando terreno marciano"
    if evento.tipo == "fim":
        return "Missao Finalizada"
    return status_atual


def _aplicar_evento(
    evento: EventoVM, particulas: list[Particula], sistema_audio: SistemaAudio
) -> float:
    # Mapa central de feedback: cada evento da VM dispara resposta visual + sonora.
    mensagem = (evento.mensagem or "").lower()

    if evento.tipo == "inicio":
        sistema_audio.tocar("boot")
        return 0.0

    if evento.tipo == "movimento":
        _emitir_poeira(particulas, evento.x, evento.y, 7, impacto=False)
        sistema_audio.tocar("move")
        return 0.0

    if evento.tipo == "giro":
        _emitir_poeira(particulas, evento.x, evento.y, 4, impacto=False)
        sistema_audio.tocar("turn")
        return 0.0

    if evento.tipo in {"colisao", "erro"} or "colisao" in mensagem or "saiu do mapa" in mensagem:
        _emitir_poeira(particulas, evento.x, evento.y, 18, impacto=True)
        sistema_audio.tocar("collision")
        return CAMERA_SHAKE_DURATION

    if evento.tipo == "fim":
        _emitir_confete_sucesso(particulas, evento.x, evento.y)
        sistema_audio.tocar("success")

    return 0.0


def _emitir_poeira(
    particulas: list[Particula], x_celula: float, y_celula: float, quantidade: int, impacto: bool
) -> None:
    rng = random.Random()
    for _ in range(quantidade):
        angulo = rng.uniform(0.0, math.tau)
        velocidade = rng.uniform(0.20, 1.05 if impacto else 0.62)
        vida = rng.uniform(0.28, 0.70 if impacto else 0.48)
        tamanho = rng.uniform(2.2, 5.0 if impacto else 3.6)
        particulas.append(
            Particula(
                x=x_celula + rng.uniform(-0.14, 0.14),
                y=y_celula + 0.38 + rng.uniform(-0.06, 0.06),
                vx=math.cos(angulo) * velocidade,
                vy=math.sin(angulo) * velocidade - (0.28 if impacto else 0.16),
                vida=vida,
                vida_total=vida,
                tamanho=tamanho,
                cor=(188, 142, 116) if impacto else (163, 122, 104),
            )
        )


def _emitir_confete_sucesso(particulas: list[Particula], x_celula: float, y_celula: float) -> None:
    rng = random.Random()
    cores = [(110, 216, 150), (116, 188, 255), (255, 223, 145)]
    for _ in range(14):
        angulo = rng.uniform(0.0, math.tau)
        velocidade = rng.uniform(0.35, 1.00)
        vida = rng.uniform(0.45, 0.95)
        particulas.append(
            Particula(
                x=x_celula + rng.uniform(-0.08, 0.08),
                y=y_celula + rng.uniform(-0.10, 0.06),
                vx=math.cos(angulo) * velocidade,
                vy=math.sin(angulo) * velocidade - 0.35,
                vida=vida,
                vida_total=vida,
                tamanho=rng.uniform(2.4, 4.4),
                cor=rng.choice(cores),
            )
        )


def _atualizar_particulas(particulas: list[Particula], dt: float) -> None:
    if not particulas:
        return

    gravidade = 0.95
    arrasto = max(0.0, 1.0 - dt * 1.8)
    i = len(particulas) - 1
    while i >= 0:
        p = particulas[i]
        p.vida -= dt
        if p.vida <= 0.0:
            particulas.pop(i)
            i -= 1
            continue
        p.x += p.vx * dt * 1.8
        p.y += p.vy * dt * 1.8
        p.vy += gravidade * dt
        p.vx *= arrasto
        p.tamanho = max(0.6, p.tamanho - dt * 2.2)
        i -= 1


def _camera_offset(dt: float, shake_restante: float) -> tuple[int, int]:
    if shake_restante <= 0.0 or dt <= 0.0:
        return (0, 0)
    intensidade = int(max(1.0, CAMERA_SHAKE_PX * (shake_restante / CAMERA_SHAKE_DURATION)))
    return (random.randint(-intensidade, intensidade), random.randint(-intensidade, intensidade))


def _criar_sprites_rover(tamanho: int) -> list[pygame.Surface]:
    base = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    cx = tamanho // 2

    corpo = pygame.Rect(int(tamanho * 0.28), int(tamanho * 0.18), int(tamanho * 0.44), int(tamanho * 0.58))
    pygame.draw.rect(base, COR_ROVER, corpo, border_radius=8)
    pygame.draw.rect(base, COR_ROVER_BORDA, corpo, 2, border_radius=8)

    cockpit = pygame.Rect(int(tamanho * 0.36), int(tamanho * 0.03), int(tamanho * 0.28), int(tamanho * 0.26))
    pygame.draw.rect(base, (164, 225, 255), cockpit, border_radius=6)
    pygame.draw.rect(base, COR_ROVER_BORDA, cockpit, 2, border_radius=6)

    pygame.draw.circle(base, (250, 238, 163), (cx, int(tamanho * 0.06)), 4)
    pygame.draw.line(base, COR_ROVER_BORDA, (cx, int(tamanho * 0.12)), (cx, int(tamanho * 0.03)), 2)

    roda_l = pygame.Rect(int(tamanho * 0.18), int(tamanho * 0.26), int(tamanho * 0.12), int(tamanho * 0.44))
    roda_r = pygame.Rect(int(tamanho * 0.70), int(tamanho * 0.26), int(tamanho * 0.12), int(tamanho * 0.44))
    pygame.draw.rect(base, (40, 52, 73), roda_l, border_radius=4)
    pygame.draw.rect(base, (40, 52, 73), roda_r, border_radius=4)
    pygame.draw.rect(base, (17, 24, 36), roda_l, 2, border_radius=4)
    pygame.draw.rect(base, (17, 24, 36), roda_r, 2, border_radius=4)

    seta = [
        (cx, int(tamanho * 0.00)),
        (int(tamanho * 0.65), int(tamanho * 0.17)),
        (int(tamanho * 0.35), int(tamanho * 0.17)),
    ]
    pygame.draw.polygon(base, (242, 160, 101), seta)
    pygame.draw.polygon(base, COR_ROVER_BORDA, seta, 2)

    sprite_norte = base
    sprite_leste = pygame.transform.rotate(base, -90)
    sprite_sul = pygame.transform.rotate(base, 180)
    sprite_oeste = pygame.transform.rotate(base, 90)
    return [sprite_norte, sprite_leste, sprite_sul, sprite_oeste]


def _gerar_estrelas(largura: int, altura: int, quantidade: int) -> list[tuple[int, int, int, float]]:
    rng = random.Random(17)
    estrelas: list[tuple[int, int, int, float]] = []
    for _ in range(quantidade):
        x = rng.randint(6, largura - 6)
        y = rng.randint(6, altura - 6)
        raio = rng.choice([1, 1, 1, 2])
        fase = rng.uniform(0.0, math.tau)
        estrelas.append((x, y, raio, fase))
    return estrelas


def _coletar_trilha(
    eventos: Sequence[EventoVM], indice_evento: int, posicao_atual: tuple[float, float]
) -> list[tuple[float, float]]:
    trilha: list[tuple[float, float]] = []
    for evento in eventos[: indice_evento + 1]:
        if not trilha or trilha[-1] != (evento.x, evento.y):
            trilha.append((evento.x, evento.y))
    if not trilha or trilha[-1] != posicao_atual:
        trilha.append(posicao_atual)
    return trilha


def _eh_movimento(origem: EventoVM, destino: EventoVM) -> bool:
    return abs(origem.x - destino.x) + abs(origem.y - destino.y) == 1


def _interpolar(origem: float, destino: float, progresso: float) -> float:
    clamped = max(0.0, min(1.0, progresso))
    return origem + (destino - origem) * clamped


def _para_pixel(
    x_celula: float, y_celula: float, camera_offset: tuple[int, int] = (0, 0)
) -> tuple[int, int]:
    return (
        int(GRID_PADDING + camera_offset[0] + x_celula * CELL_SIZE + CELL_SIZE / 2),
        int(TOP_HUD + camera_offset[1] + y_celula * CELL_SIZE + CELL_SIZE / 2),
    )


def _cor_status(status: str) -> tuple[int, int, int]:
    status_l = status.lower()
    if "colisao" in status_l or "saiu do mapa" in status_l or "erro" in status_l:
        return COR_STATUS_ALERTA
    if "finalizada" in status_l:
        return COR_STATUS_OK
    return COR_STATUS_EXEC
