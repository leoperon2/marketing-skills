import numpy as np
from PIL import Image
def feats(path_or_im):
    im=path_or_im if hasattr(path_or_im,'size') else Image.open(path_or_im)
    im=im.convert('RGB').copy(); im.thumbnail((200,200)); a=np.asarray(im).astype(np.int32)
    q=(a//16).reshape(-1,3); key=q[:,0]*256+q[:,1]*16+q[:,2]
    cnt=np.sort(np.bincount(key))[::-1]; tot=cnt.sum()
    top3=cnt[:3].sum()/tot
    c80=int(np.searchsorted(np.cumsum(cnt)/tot,0.8))+1
    g=np.asarray(im.convert('L'),dtype=np.float32)
    flat=(np.abs(np.diff(g,axis=1))<2).mean()
    return top3,c80,flat
