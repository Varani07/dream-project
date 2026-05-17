from textual.containers import Grid
from textual.widgets import Button

from core.entity.components import WorldKnowledgeComponent, LocationComponent
from core.world import Region, Location


class MiniMap(Grid):
    def __init__(
            self,world_region:Region,location_comp:LocationComponent,
            world_knowledge_comp:WorldKnowledgeComponent,**kw):
        
        super().__init__(**kw)
        self.drawing = False
        self.build_info(world_region,location_comp,world_knowledge_comp)

    def compose(self):
        for y in range(self.rows):
            for x in range(self.cols):
                yield Button(self._label(x, y), id=f"cell_{x}_{y}", classes="cell_btn")

    def _label(self, x: int, y: int) -> str:
        if not self.inside_location:
            place = self.world_region.get_location((x,y))
        else:
            place = self.place.get_room((x,y))
            
        if (x, y) == self.current:
            return "[red]x[/]"
        if (x, y) in self.known and place:
            return f"[{place.color}]{place.glyph}[/]"
        if not self.inside_location or (self.inside_location and (x,y) in self.possible_rooms):
            return "[dim]?[/]"
        else:
            return "[dim]░[/]"

    def update(
            self, known: set[tuple[int, int]],
            current: tuple[int, int]) -> None:
        
        self.known = known
        self.current = current
        
        cells = self.query(".cell_btn")

        for btn in cells:
            if btn.id is None:
                continue
            _,x_str,y_str=btn.id.split("_")
            x,y=int(x_str),int(y_str)
            btn.label = self._label(x, y) #type: ignore

    async def rebuild_map(
            self,region:Region,location_comp:LocationComponent,
            world_knowledge_comp:WorldKnowledgeComponent) -> None:
        
        if self.drawing:
            return
        self.drawing=True

        try:
            self.build_info(region,location_comp,world_knowledge_comp)
            await self.query(".cell_btn").remove()
            new_btns = []
            for y in range(self.rows):
                for x in range(self.cols):
                    new_btns.append(
                        Button(self._label(x, y), id=f"cell_{x}_{y}", classes="cell_btn")
                    )
            await self.mount(*new_btns)
        finally:
            self.drawing=False

    def build_info(
            self,region:Region,location_comp:LocationComponent,
            world_knowledge_comp:WorldKnowledgeComponent):
    
        self.world_region = region
        place = self.world_region.get_location(location_comp.xy)
        assert place is not None
        self.place:Location=place
        self.inside_location:bool=location_comp.inside_location
        self.possible_rooms = set()

        if not location_comp.inside_location:
            self.current = location_comp.xy
            self.known = world_knowledge_comp.get_known_places(self.world_region.name)
            self.cols, self.rows = region.locations_count
        else:
            self.current = location_comp.room
            self.known = world_knowledge_comp.get_known_rooms(
                region_name=self.world_region.name,
                xy=location_comp.xy
            )
            self.cols, self.rows = self.place.rooms_count
            self.possible_rooms = self.place.possible_rooms

        self.cols, self.rows = self.cols+1, self.rows+1

        self.styles.grid_size_columns = self.cols
        self.styles.grid_size_rows = self.rows
        self.styles.grid_columns = ("6 " * self.cols).strip()
        self.styles.grid_rows = ("3 " * self.rows).strip()
        