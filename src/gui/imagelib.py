import sys
import os
import stat
import traceback
import Image     # PIL

import mevas

import config
import util
import util.thumbnail
import theme_engine

import logging
log = logging.getLogger('gui')

def resizebitmap(image, width=None, height=None):
    image_w, image_h = image.width, image.height
    if width == None:
        # calculate width
        width = (height * float(image_w)) / float(image_h)
    if height == None:
        # calculate width
        height = (width * float(image_h)) / float(image_w)
    return mevas.imagelib.scale(image, (width, height))


def rotate(*arg1, **arg2):
    return mevas.imagelib.rotate(*arg1, **arg2)


def scale(*arg1, **arg2):
    return mevas.imagelib.scale(*arg1, **arg2)


def load(url, size=None, cache=False, vfs_save=False):
    """
    Load a bitmap and return the image object.
    If width and height are given, the image is scaled to that. Setting
    only width or height will keep aspect ratio.
    If vfs_save is true, the so scaled bitmap will be stored in the vfs for
    future use.
    """
    if size == None:
        width, height = None, None
    else:
        width, height = size
        
    try:
        # maybe the image is an image object from PIL
        image = mevas.imagelib.new(url.size, url.tostring(), url.mode)

        # scale the image if needed
        if width != None or height != None:
            image = resizebitmap(image, width, height)
        return image
    except:
        # no, it is not
        pass
    
    if url.find('/') == -1 and url.find('.') == -1:
        # this looks like a 'theme' image
        surl = theme_engine.get_theme().get_image(url)
        if surl:
            url = surl
    if cache:
        # first check the cache
        if width != None or height != None:
            key = 'scaled://%s-%s-%s' % (url, width, height)
        else:
            key = url
        key += os.stat(url)[stat.ST_MTIME]
        
        s = cache[key]
        if s:
            return s

    if vfs_save and (width == None or height == None):
        vfs_save = False

    # not in cache, load it
    filename = os.path.abspath(url)

    if vfs_save:
        vfs_save = vfs.getoverlay('%s.raw-%sx%s' % (filename, width, height))
        try:
            if os.stat(vfs_save)[stat.ST_MTIME] > \
                   os.stat(filename)[stat.ST_MTIME]:
                f = open(vfs_save, 'r')
                image = mevas.imagelib.new((width, height), f.read(), 'RGBA')
                f.close()
                if cache:
                    cache[key] = image
                return image
        except:
            pass

    if not os.path.isfile(filename):
        filename = os.path.join(config.IMAGE_DIR, url[8:])

    if not os.path.isfile(filename):
        log.error('osd.py: Bitmap file "%s" doesnt exist!' % filename)
        return None

    try:
        try:
            image = mevas.imagelib.open(filename)
        except Exception, e:
            log.info('imagelib load problem: %s - trying Imaging' % e)
            i = Image.open(filename)
            image = mevas.imagelib.new(i.tostring(), i.size, i.mode)

    except:
        log.exception('Unknown Problem while loading image %s' % String(url))
        return None

    # scale the image if needed
    if width != None or height != None:
        image = resizebitmap(image, width, height)

    if vfs_save:
        f = vfs.open(vfs_save, 'w')
        f.write(image.get_raw_data('RGBA'))
        f.close()

    if cache:
        cache[key] = image
    return image



item_imagecache = util.objectcache.ObjectCache(30, desc='item_image')

def item_image(item, size, icon_dir, force=False, cache=True):
    """
    Return the image for an item. This function uses internal caches and
    can also return a mimetype image if no image is found and force is True
    """
    if cache == True:
        cache = item_imagecache
        
    width, height = size
    try:
        type = item.display_type
    except:
        try:
            type = item.info['mime'].replace('/', '_')
        except:
            type = item.type

    if isinstance(item.image, (str, unicode)):
        key = '%s-%s-%s-%s-%s-%s-%s-%s' \
              % (icon_dir, item.image, type, item.type, width, height, force,
                 os.stat(item.image)[stat.ST_MTIME])
                
        if item['rotation']:
            key = '%s-%s' % (key, item['rotation'])
            
        if item.media and item.media.item == item:
            key = '%s-%s' % (key, item.media)
        
        image = cache[key]

        if image:
            return image

    image     = None
    imagefile = None
    
    if item.image:
        try:
            # load the thumbnail
            image = util.thumbnail.load(item.image)
        except:
            # maybe image is something else (like already an image object)
            image = load(item.image)

    if image:
        if item['rotation']:
            image.rotate(item['rotation'])
    else:
        if not force:
            return None

        if hasattr(item, 'media') and item.media and item.media.item == item and \
           os.path.isfile('%s/mimetypes/%s.png' % (icon_dir, item.media.type)):
            imagefile = '%s/mimetypes/%s.png' % (icon_dir, item.media.type)
            

        elif item.type == 'dir':
            if os.path.isfile('%s/mimetypes/folder_%s.png' % \
                              (icon_dir, item.display_type)):
                imagefile = '%s/mimetypes/folder_%s.png' % \
                            (icon_dir, item.display_type)
            else:
                imagefile = '%s/mimetypes/folder.png' % icon_dir
    
        elif item.type == 'playlist':
            if item.parent and os.path.isfile('%s/mimetypes/playlist_%s.png' % \
                                              (icon_dir, item.parent.display_type)):
                imagefile = '%s/mimetypes/playlist_%s.png' % \
                            (icon_dir, item.parent.display_type)
            else:
                imagefile = '%s/mimetypes/playlist.png' % icon_dir

        elif os.path.isfile('%s/mimetypes/%s.png' % (icon_dir, type)):
            imagefile = '%s/mimetypes/%s.png' % (icon_dir, type)

        elif os.path.isfile('%s/mimetypes/%s.png' % (icon_dir, item.type)):
            imagefile = '%s/mimetypes/%s.png' % (icon_dir, item.type)

        elif os.path.isfile('%s/mimetypes/unknown.png' % icon_dir):
            imagefile = '%s/mimetypes/unknown.png' % icon_dir
            
        if not imagefile:
            return None

        # load the thumbnail
        image = util.thumbnail.load(imagefile)
            
        if not image:
            return None

    if type and len(type) > 4:
        type = type[:5]
        
    i_w = image.width
    i_h = image.height
    aspect = float(i_h)/i_w

    if type == 'audio' and aspect < 1.3 and aspect > 0.8:
        # this is an audio cover
        m = min(height, width)
        i_w = m
        i_h = m
        
    elif type == 'video' and aspect > 1.3 and aspect < 1.6:
        # video cover, set aspect 7:5
        i_w = 5
        i_h = 7
        
    if int(float(width * i_h) / i_w) > height:
        width = int(float(height * i_w) / i_h)
    else:
        height = int(float(width * i_h) / i_w)

    image.scale((width, height))
    if isinstance(item.image, (str, unicode)):
        cache[key] = image
    return image
