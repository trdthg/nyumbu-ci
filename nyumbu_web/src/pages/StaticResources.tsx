import { useEffect, useState } from 'react';
import { baseUrl } from '../api';

export default function StaticResources(props: { url: string }) {
    const [resource, setResource] = useState<string>();
    const [img, setImg] = useState(false);
    useEffect(() => {
        if (props.url.endsWith('.png') || props.url.endsWith('.jpg')) {
            setImg(true);
            return;
        }
        fetch(`${baseUrl}/${props.url}`)
            .then((res) => res.text())
            .then((text) => setResource(text));
    }, [props.url]);

    return img ? <img src={`${baseUrl}/${props.url}`} /> : <>{resource}</>;
}
