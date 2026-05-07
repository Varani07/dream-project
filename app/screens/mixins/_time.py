from __future__ import annotations


class TempoMixin:
    def _atualizar_relogio_principal(self) -> None:
        self.atualizar_status()
        self.atualizar_mapa()

    def _iniciar_tempo_auto(self) -> None:
        if self._tempo_auto_timer is not None:
            return
        self._tempo_auto_timer = self.set_interval(0.4, self._tempo_auto_tick)

    def _parar_tempo_auto(self) -> None:
        if self._tempo_auto_timer is not None:
            self._tempo_auto_timer.stop()
            self._tempo_auto_timer = None

    def _tempo_auto_tick(self) -> None:
        self.time_manager.avancar_simples(1, motivo="auto")
        self._atualizar_relogio_principal()

    def _abrir_modal_avancar_tempo(self) -> None:
        from app.widgets.modais import AvancarTempoModal

        def callback(minutos:int|None) -> None:
            if not minutos or minutos <= 0:
                return
            self._avancar_visualmente(minutos, motivo="manual")
        self.app.push_screen(AvancarTempoModal(valor_inicial=5), callback)

    def _avancar_visualmente(
            self, minutos: int, motivo: str = "manual",
            on_done=None) -> None:
        
        if minutos <= 0:
            if on_done:
                on_done()
            return
        
        if getattr(self, "_tempo_play_timer", None) is not None:
            try:
                self._tempo_play_timer.stop()
            except Exception:
                pass
            self._tempo_play_timer = None

        self._tempo_play_restantes = int(minutos)
        self._tempo_play_callback = on_done
        self.time_manager.in_action = True

        def tick() -> None:
            if self._tempo_play_restantes <= 0:
                if self._tempo_play_timer:
                    self._tempo_play_timer.stop()
                self._tempo_play_timer = None
                self.time_manager.in_action = False
                cb = getattr(self, "_tempo_play_callback", None)
                self._tempo_play_callback = None
                if cb:
                    try:
                        cb()
                    except Exception:
                        pass
                return
            self.time_manager.avancar_simples(1, motivo=motivo)
            self._tempo_play_restantes -= 1
            self._atualizar_relogio_principal()

        # 50ms entre passos: 60 min em 3s, 480 min em 24s.
        self._tempo_play_timer = self.set_interval(0.05, tick)

    def _acao_com_tempo(self, minutos: int, motivo: str,
                        on_done=None) -> None:
        """API que ações do player chamam.

        - 1 min: avanço síncrono (delay imperceptível).
        - 2+ min: playback visual.

        Chame este método em vez de `avancar_em_passos` direto sempre que
        uma ação do player consumir tempo. Assim o jogador VÊ a ação
        durar — a diferença entre "comer um pão" (5 min) e "cozinhar"
        (45 min) deixa de ser só um número no relógio.
        """
        if minutos <= 1:
            self.time_manager.avancar_em_passos(max(1, minutos), motivo=motivo)
            self._atualizar_relogio_principal()
            if on_done:
                on_done()
            return
        self._avancar_visualmente(minutos, motivo=motivo, on_done=on_done)