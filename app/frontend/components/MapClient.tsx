"use client";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import type { GeoJSON as GeoJSONT } from "geojson";

export default function MapClient({ data }: { data: GeoJSONT }) {
  return (
    <div style={{height:400, width:"100%", borderRadius:12, overflow:"hidden"}}>
      <MapContainer center={[5.2,-0.1]} zoom={6} style={{height:"100%", width:"100%"}}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <GeoJSON data={data} />
      </MapContainer>
    </div>
  );
}
